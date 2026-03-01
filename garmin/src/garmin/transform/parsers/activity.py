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
        filename = activity_file.stem
        parts = filename.split("_")
        activity_id = parts[2]
        activity_name = metadata.activity_mapping.get(activity_id)
        print(f"Processing {activity_name}")
        fit = fitdecode.FitReader(str(activity_file), processor=fitdecode.StandardUnitsDataProcessor())

        device_id = None
        session_info = None
        last_status = None
        last_user_metrics = None

        record_count = 0
        hr_values = []
        distance_values = []

        device_id: str | None
        for frame in fit:
            # Only care about data messages (not definitions or headers)
            if isinstance(frame, fitdecode.records.FitDataMessage):
                did = extract_device_id(frame)
                if did:
                    device_id = did

                status = extract_device_statuse(frame)
                if status:
                    last_status = status

                metrics = extract_user_metrics(frame)
                if metrics:
                    last_user_metrics = metrics

                activity = extract_activity_session(frame)
                if activity:
                    session_info = activity

                record = extract_record(frame)
                if record:
                    record_count += 1

                    if record["heart_rate"] is not None:
                        hr_values.append(record["heart_rate"])

                    if record["distance"] is not None:
                        distance_values.append(record["distance"])
                # if activity:
                #     print(activity)
                # for field in frame.fields:
                #     print(f"  {field.name}: {field.value}")
        print("\n========== ACTIVITY SUMMARY ==========")
        print("File:", activity_file.name)
        print("Activity Name:", activity_name)
        print("Device ID:", device_id)

        print("\n--- Records ---")
        print("Total records:", record_count)

        if hr_values:
            print("Avg HR:", sum(hr_values) / len(hr_values))
            print("Min HR:", min(hr_values))
            print("Max HR:", max(hr_values))
        else:
            print("No heart rate data")

        if distance_values:
            print("Final Distance:", max(distance_values))
        else:
            print("No distance data")

        print("\n--- Session ---")
        if session_info:
            print("Sport:", session_info["sport"])
            print("Sub-sport:", session_info["sub_sport"])
            print("Total Distance:", session_info["total_distance"])
            print("Start:", session_info["start_time"])
            print("End (epoch):", session_info["end_time"])
        else:
            print("No session info")

        print("\n--- Device Status ---")
        if last_status:
            print("Battery:", last_status["battery_level"])
            print("Temperature:", last_status["temperature"])
        else:
            print("No device status")

        print("\n--- User Metrics ---")
        if last_user_metrics:
            print("VO2 Max:", last_user_metrics["vo2_max"])
            print("Max HR:", last_user_metrics["max_hr"])
            print("LTHR:", last_user_metrics["lthr"])
        else:
            print("No user metrics")

        print("======================================\n")


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
    cadence = frame.get_field("cadence") if frame.has_field("cadence") else None
    vertical_oscillation = frame.get_field("vertical_oscillation") if frame.has_field("vertical_oscillation") else None
    speed = frame.get_field("enhanced_speed") if frame.has_field("enhanced_speed") else None
    step_length = frame.get_field("step_length") if frame.has_field("step_length") else None
    stance_time = frame.get_field("stance_time") if frame.has_field("stance_time") else None
    body_battery = frame.get_field(143)  # unknown_143

    return {
        "timestamp": timestamp.value if timestamp else None,  # datetime in utc
        "heart_rate": heart_rate.value if heart_rate else None,
        "distance": distance.value if distance else None,  # in km
        "body_battery": body_battery.value if body_battery else None,
        "cadence": cadence.value if cadence else None,
        "speed": speed.value if speed else None,
        "step_length": step_length.value if step_length else None,
        "stance_time": stance_time.value if stance_time else None,
        "vertical_oscillation": vertical_oscillation.value if vertical_oscillation else None,
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
