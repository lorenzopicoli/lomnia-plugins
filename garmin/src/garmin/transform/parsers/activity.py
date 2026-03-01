from datetime import datetime, timedelta, timezone
from pathlib import Path

import fitdecode
from attr import dataclass

from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.activity import (
    ActivityDeviceStatus,
    ActivityRecord,
    ActivitySession,
    ActivityTrainingSettings,
    ActivityUserMetrics,
)


@dataclass
class FITResult:
    device_id: str
    device_statuses: list[ActivityDeviceStatus]
    metrics: list[ActivityUserMetrics]
    training_settings: list[ActivityTrainingSettings]
    sessions: list[ActivitySession]
    records: list[ActivityRecord]


def process_activity_file(activity_file: Path, metadata: TransformRunMetadata):
    filename = activity_file.stem
    parts = filename.split("_")
    fit = fitdecode.FitReader(str(activity_file), processor=fitdecode.StandardUnitsDataProcessor())

    activity_id = parts[2]
    activity_name = metadata.activity_mapping.get(activity_id)
    print("Activity Name:", activity_name)

    device_id: str
    device_statuses: list[ActivityDeviceStatus] = []
    metrics: list[ActivityUserMetrics] = []
    training_settings: list[ActivityTrainingSettings] = []
    sessions: list[ActivitySession] = []
    records: list[ActivityRecord] = []

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

    return FITResult(
        device_id=device_id,
        device_statuses=device_statuses,
        metrics=metrics,
        training_settings=training_settings,
        sessions=sessions,
        records=records,
    )


def extract_device_id(frame: fitdecode.records.FitDataMessage) -> str | None:
    if frame.name == "file_id":
        return frame.get_field("serial_number").value

    return None


def extract_user_metrics(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityUserMetrics | None:
    if frame.name != "unknown_79":
        return None

    timestamp = frame.get_field(253)
    vo2_max = frame.get_field(0)
    max_hr = frame.get_field(6)
    lthr = frame.get_field(11)
    return ActivityUserMetrics(
        timestamp=datetime.fromtimestamp(timestamp.value, tz=timezone.utc),
        vo2_max=vo2_max.value if vo2_max else None,
        max_hr=max_hr.value if max_hr else None,
        lthr=lthr.value if lthr else None,
    )


def extract_device_status(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityDeviceStatus | None:
    if frame.name != "unknown_104":
        return None

    timestamp = frame.get_field(253)
    battery = frame.get_field(2)
    temperature = frame.get_field(3)

    return ActivityDeviceStatus(
        timestamp=datetime.fromtimestamp(timestamp.value, tz=timezone.utc),
        battery_level=battery.value if battery else None,
        temperature=temperature.value if temperature else None,
    )


def extract_training_settings(
    frame: fitdecode.records.FitDataMessage,
) -> ActivityTrainingSettings | None:
    if frame.name != "training_settings":
        return None

    self_evaluation = frame.get_field(93)

    return ActivityTrainingSettings(self_evaluation=self_evaluation.value if self_evaluation else None)


def extract_record(frame: fitdecode.records.FitDataMessage) -> ActivityRecord | None:
    if frame.name != "record":
        return None

    timestamp = frame.get_field("timestamp")
    heart_rate = frame.get_field("heart_rate")
    lat = frame.get_field("position_lat") if frame.has_field("position_lat") else None
    lng = frame.get_field("position_lng") if frame.has_field("position_lng") else None
    altitude = frame.get_field("enhanced_altitude") if frame.has_field("enhanced_altitude") else None
    distance = frame.get_field("distance") if frame.has_field("distance") else None
    cadence = frame.get_field("cadence") if frame.has_field("cadence") else None
    vertical_oscillation = frame.get_field("vertical_oscillation") if frame.has_field("vertical_oscillation") else None
    speed = frame.get_field("enhanced_speed") if frame.has_field("enhanced_speed") else None
    step_length = frame.get_field("step_length") if frame.has_field("step_length") else None
    stance_time = frame.get_field("stance_time") if frame.has_field("stance_time") else None
    body_battery = frame.get_field(143)  # unknown_143

    return ActivityRecord(
        timestamp=timestamp.value if timestamp else None,
        heart_rate=heart_rate.value if heart_rate else None,
        distance=distance.value if distance else None,
        body_battery=body_battery.value if body_battery else None,
        cadence=cadence.value if cadence else None,
        speed=speed.value if speed else None,
        step_length=step_length.value if step_length else None,
        stance_time=stance_time.value if stance_time else None,
        vertical_oscillation=vertical_oscillation.value if vertical_oscillation else None,
        lat=lat.value if lat else None,
        lng=lng.value if lng else None,
        altitude=altitude.value if altitude else None,
    )


def extract_activity_session(frame: fitdecode.records.FitDataMessage) -> ActivitySession | None:
    if frame.name != "session":
        return None

    timestamp: datetime = frame.get_field("timestamp").value
    sub_sport = frame.get_field("sub_sport")
    sport = frame.get_field("sport")
    start_time = frame.get_field("start_time")
    total_time_elapsed = frame.get_field(7)
    end_date = timestamp + timedelta(seconds=total_time_elapsed.value)
    total_distance = frame.get_field("total_distance")
    return ActivitySession(
        timestamp=timestamp,
        sport=sport.value if sport else None,
        sub_sport=sub_sport.value if sub_sport else None,
        start_time=start_time.value if start_time else None,
        end_time=end_date,
        total_distance=total_distance.value if total_distance else None,
    )
