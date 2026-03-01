from pathlib import Path
from typing import Any

import fitdecode

from garmin.config import ACTIVITY_FOLDER
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.schemas import Schemas


def process_activity_files(tmp_path: Path, metadata: TransformRunMetadata, schemas: Schemas):
    activity_dir = Path(tmp_path) / ACTIVITY_FOLDER
    all_activities: dict[str, Any] = {}

    for activity_file in activity_dir.glob("*.fit"):
        print("Found activity file:", activity_file)
        # fitfile = fitparse.FitFile(
        #     str(activity_file),
        #     data_processor=fitparse.StandardUnitsDataProcessor(),
        # )
        fit = fitdecode.FitReader(str(activity_file), processor=fitdecode.StandardUnitsDataProcessor())
        device_id: str | None
        for frame in fit:
            # Only care about data messages (not definitions or headers)
            if isinstance(frame, fitdecode.records.FitDataMessage):
                device_id = extract_device_id(frame)
                statuses = extract_device_statuse(frame)
                records = extract_record(frame)
                user_metrics = extract_user_metrics(frame)
                activity = extract_activity_session(frame)
                if activity:
                    print(activity)
                # for field in frame.fields:
                #     print(f"  {field.name}: {field.value}")
        # for record in fitfile.get_messages("record"):
        #     record: Any = record
        #
        #     values = record.get_values()
        #
        #     print(values)
        print("Device:", device_id)


def extract_device_id(frame: fitdecode.records.FitDataMessage) -> str | None:
    if frame.name == "file_id":
        return frame.get_field("serial_number").value

    return None


def extract_user_metrics(
    frame: fitdecode.records.FitDataMessage,
) -> dict[str, object] | None:
    if frame.name != "unknown_79":
        return None

    timestamp = frame.get_field(253)  # timestamp
    vo2_max = frame.get_field(0)
    max_hr = frame.get_field(6)
    lthr = frame.get_field(11)

    return {
        "timestamp": timestamp.value,  # epoch
        "vo2_max": vo2_max.value,
        "max_hr": max_hr.value,
        "lthr": lthr.value,
    }


def extract_device_statuse(
    frame: fitdecode.records.FitDataMessage,
) -> dict[str, object] | None:
    if frame.name != "unknown_104":
        return None

    timestamp = frame.get_field(253)  # timestamp
    batterie = frame.get_field(2)  # batt level
    temperature = frame.get_field(3)  # temp

    return {
        "timestamp": timestamp.value,  # epoch
        "battery_level": batterie.value,
        "temperature": temperature.value,
    }


def extract_record(frame: fitdecode.records.FitDataMessage) -> dict[str, object] | None:
    if frame.name != "record":
        return None

    timestamp = frame.get_field("timestamp")
    heart_rate = frame.get_field("heart_rate")
    distance = frame.get_field("distance") if frame.has_field("distance") else None
    body_battery = frame.get_field(143)  # unknown_143

    return {
        "timestamp": timestamp.value if timestamp else None,  # datetime in utc
        "heart_rate": heart_rate.value if heart_rate else None,
        "distance": distance.value if distance else None,  # in km
        "body_battery": body_battery.value if body_battery else None,
    }


def extract_activity_session(frame: fitdecode.records.FitDataMessage) -> dict[str, object] | None:
    if frame.name != "session":
        return None

    timestamp = frame.get_field("timestamp")
    sub_sport = frame.get_field("sub_sport")
    sport = frame.get_field("sport")
    start_time = frame.get_field("start_time")  # datetime in utc
    total_time_elapsed = frame.get_field(7)  # in seconds
    total_distance = frame.get_field("total_distance")

    return {
        "timestamp": timestamp.value if timestamp else None,  # datetime in utc
        "sport": sport.value,
        "sub_sport": sub_sport.value,
        "start_time": start_time.value,
        "end_time": start_time.raw_value + total_time_elapsed.value,  # epoch
        "total_distance": total_distance.value,
    }
