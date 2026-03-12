from datetime import datetime, timedelta, timezone
from pathlib import Path

import fitdecode
from attr import dataclass

from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.activity import (
    ActivityDeviceStatus,
    ActivityLap,
    ActivityRecord,
    ActivitySession,
    ActivityTrainingSettings,
    ActivityUserMetrics,
)


@dataclass
class FITResult:
    activity_name: str
    device_id: str
    device_statuses: list[ActivityDeviceStatus]
    metrics: list[ActivityUserMetrics]
    training_settings: list[ActivityTrainingSettings]
    sessions: list[ActivitySession]
    records: list[ActivityRecord]
    laps: list[ActivityLap]


def process_activity_file(activity_file: Path, metadata: TransformRunMetadata):
    filename = activity_file.stem
    parts = filename.split("_")
    fit = fitdecode.FitReader(str(activity_file), processor=fitdecode.StandardUnitsDataProcessor())

    activity_id = parts[2]
    activity_name = metadata.activity_mapping.get(activity_id)
    print("Activity Name:", activity_name)

    if activity_name is None:
        print("Skipping activity for not having a name")
        raise

    device_id: str
    device_statuses: list[ActivityDeviceStatus] = []
    metrics: list[ActivityUserMetrics] = []
    training_settings: list[ActivityTrainingSettings] = []
    sessions: list[ActivitySession] = []
    records: list[ActivityRecord] = []
    laps: list[ActivityLap] = []

    for frame in fit:
        # Only care about data messages (not definitions or headers)
        if isinstance(frame, fitdecode.records.FitDataMessage):
            if local_device_id := extract_device_id(frame):
                device_id = local_device_id

            if status := extract_device_status(frame):
                device_statuses.append(status)

            if local_metrics := extract_user_metrics(frame):
                metrics.append(local_metrics)

            if session := extract_activity_session(frame):
                sessions.append(session)

            if settings_info := extract_training_settings(frame):
                training_settings.append(settings_info)

            if record := extract_record(frame):
                records.append(record)

            if lap := extract_lap(frame):
                laps.append(lap)

            # if frame.name == "lap":
            #     for field in frame.fields:
            #         print(f"  {field.name}: {field.value}")

    return FITResult(
        activity_name=activity_name,
        device_id=device_id,
        device_statuses=device_statuses,
        metrics=metrics,
        training_settings=training_settings,
        sessions=sessions,
        records=records,
        laps=laps,
    )


def field_value(frame, name):
    if not frame.has_field(name):
        return None
    field = frame.get_field(name)
    return field.value if field else None


def extract_device_id(frame: fitdecode.records.FitDataMessage) -> str | None:
    if frame.name != "file_id":
        return None

    return field_value(frame, "serial_number")


def extract_user_metrics(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityUserMetrics | None:
    if frame.name != "unknown_79":
        return None

    timestamp = field_value(frame, 253)
    if timestamp is None:
        return None

    return ActivityUserMetrics(
        timestamp=datetime.fromtimestamp(timestamp, tz=timezone.utc),
        vo2_max=field_value(frame, 0),
        max_hr=field_value(frame, 6),
        lthr=field_value(frame, 11),
    )


def extract_device_status(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityDeviceStatus | None:
    if frame.name != "unknown_104":
        return None

    timestamp = field_value(frame, 253)
    if timestamp is None:
        return None

    return ActivityDeviceStatus(
        timestamp=datetime.fromtimestamp(timestamp, tz=timezone.utc),
        battery_level=field_value(frame, 2),
        temperature=field_value(frame, 3),
    )


def extract_training_settings(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityTrainingSettings | None:
    if frame.name != "training_settings":
        return None

    return ActivityTrainingSettings(
        self_evaluation=field_value(frame, 93),
    )


def extract_record(frame: fitdecode.records.FitDataMessage) -> ActivityRecord | None:
    if frame.name != "record":
        return None

    return ActivityRecord(
        timestamp=field_value(frame, "timestamp"),
        heart_rate=field_value(frame, "heart_rate"),
        distance=field_value(frame, "distance"),
        body_battery=field_value(frame, 143),  # unknown_143
        cadence=field_value(frame, "cadence"),
        speed=field_value(frame, "enhanced_speed"),
        step_length=field_value(frame, "step_length"),
        stance_time=field_value(frame, "stance_time"),
        vertical_oscillation=field_value(frame, "vertical_oscillation"),
        lat=field_value(frame, "position_lat"),
        lng=field_value(frame, "position_lng"),
        altitude=field_value(frame, "enhanced_altitude"),
    )


def extract_activity_session(frame: fitdecode.records.FitDataMessage) -> ActivitySession | None:
    if frame.name != "session":
        return None

    timestamp = field_value(frame, "timestamp")
    total_time_elapsed = field_value(frame, 7)

    if timestamp is None:
        return None

    end_time = timestamp + timedelta(seconds=total_time_elapsed) if total_time_elapsed is not None else None

    return ActivitySession(
        timestamp=timestamp,
        sport=field_value(frame, "sport"),
        sub_sport=field_value(frame, "sub_sport"),
        start_time=field_value(frame, "start_time"),
        end_time=end_time,
        total_distance=field_value(frame, "total_distance"),
        avg_cadence=field_value(frame, "avg_cadence"),
        avg_heart_rate=field_value(frame, "avg_heart_rate"),
        avg_speed=field_value(frame, "enhanced_avg_speed"),
    )


def extract_lap(frame: fitdecode.records.FitDataMessage) -> ActivityLap | None:
    if frame.name != "lap":
        return None
    start_time = field_value(frame, "start_time")
    total_time_elapsed = field_value(frame, "total_timer_time")
    end_time = None
    if start_time and total_time_elapsed:
        end_time = start_time + timedelta(seconds=total_time_elapsed)
    total_distance = field_value(frame, "total_distance")
    total_strides = field_value(frame, "total_strides")

    avg_speed = field_value(frame, "enhanced_avg_speed")
    max_speed = field_value(frame, "enhanced_max_speed")

    avg_vertical_oscillation = field_value(frame, "avg_vertical_oscillation")
    avg_stance_time = field_value(frame, "avg_stance_time")
    avg_step_length = field_value(frame, "avg_step_length")

    avg_heart_rate = field_value(frame, "avg_heart_rate")
    max_heart_rate = field_value(frame, "max_heart_rate")

    avg_running_cadence = field_value(frame, "avg_running_cadence")
    max_running_cadence = field_value(frame, "max_running_cadence")

    return ActivityLap(
        start_time=start_time,
        end_time=end_time,
        total_distance=total_distance,
        total_strides=total_strides,
        avg_speed=avg_speed,
        max_speed=max_speed,
        avg_vertical_oscillation=avg_vertical_oscillation,
        avg_stance_time=avg_stance_time,
        avg_step_length=avg_step_length,
        avg_heart_rate=avg_heart_rate,
        max_heart_rate=max_heart_rate,
        avg_cadence=avg_running_cadence,
        max_cadence=max_running_cadence,
        duration=total_time_elapsed,
    )
