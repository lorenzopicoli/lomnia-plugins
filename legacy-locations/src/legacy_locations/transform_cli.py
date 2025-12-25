import argparse
import gzip
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import jsonlines
import jsonschema
from dotenv import load_dotenv

from legacy_locations.common.helpers import iso_utc
from legacy_locations.transform.helpers import get_file_name
from legacy_locations.transform.transformer_config import (
    DEVICE_SCHEMA_URL,
    DEVICE_STATUS_SCHEMA_URL,
    LOCATION_SCHEMA_URL,
    TransformerArgs,
    TransformerEnvVars,
    load_schema,
)
from legacy_locations.transform.transformer_run_metadata import TransformRunMetadata

load_dotenv()


run_metadata = TransformRunMetadata()
run_metadata.start()

run_metadata.set_schema(
    entity="location", version="1")
run_metadata.set_schema(
    entity="device", version="1")
run_metadata.set_schema(
    entity="deviceStatus", version="1")


def is_owntracks_raw(raw: dict) -> bool:
    return "lat" in raw and "lon" in raw and "tst" in raw


class FailedToTransform(ValueError):
    def __init__(self, value):
        super().__init__(value)


def parse_transform_args() -> TransformerArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--out_dir",
        required=True,
        type=Path,
        help="Output directory path"
    )

    parser.add_argument(
        "--in_dir",
        required=True,
        type=Path,
        help="Input directory path"
    )

    parsed = parser.parse_args()
    return TransformerArgs(in_dir=parsed.in_dir, out_dir=parsed.out_dir)


def iter_legacy_rows(in_dir: Path):
    for path in in_dir.iterdir():
        if path.is_file() and '.jsonl' in path.suffixes and '.gz' in path.suffixes:
            run_metadata.add_input(path)
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for line in f:
                    yield json.loads(line)


def normalize_location(row: dict) -> dict:
    raw = row["raw"]
    if "lat" in raw and "lon" in raw:
        ts = datetime.fromtimestamp(raw["tst"], tz=timezone.utc)
        return {
            "lat": raw["lat"],
            "lng": raw["lon"],
            "accuracy": raw.get("acc"),
            "verticalAccuracy": raw.get("vac"),
            "velocity": raw.get("vel"),
            "altitude": raw.get("alt"),
            "battery": raw.get("batt"),
            "batteryStatus": raw.get("batt"),
            "connectionStatus": raw.get("conn"),
            "wifiSSID": raw.get("SSID"),
            "timezone": raw.get("tzname"),
            "recorded_at": ts,
            "source": "legacy_locations",
            "topic": raw.get("topic"),
        }

    ts = datetime.fromisoformat(raw["timestamp"].replace("Z", "+00:00"))
    return {
        "lat": raw["latitude"],
        "lng": raw["longitude"],
        "accuracy": raw.get("accuracy"),
        "verticalAccuracy": raw.get("verticalAccuracy"),
        "velocity": raw.get("velocity"),
        "altitude": raw.get("altitude"),
        "battery": raw.get("battery"),
        "batteryStatus": raw.get("batteryStatus"),
        "connectionStatus": raw.get("connectionStatus"),
        "wifiSSID": raw.get("wifiSSID"),
        "timezone": row.get("timezone"),
        "recorded_at": ts,
        "source": "legacy_locations",
        "topic": raw.get("originalPublishTopic"),
    }


def transform_location(normalized: dict, device: str, schema: dict) -> dict:
    transformed = {
        "id": str(uuid.uuid4()),
        "entityType": "location",
        "version": run_metadata.schemas["location"],
        "deviceId": device,
        "source": normalized["source"],
        "accuracy": normalized["accuracy"],
        "verticalAccuracy": normalized["verticalAccuracy"],
        "velocity": normalized["velocity"],
        "altitude": normalized["altitude"],
        "location": {
            "lat": normalized["lat"],
            "lng": normalized["lng"],
        },
        "timezone": normalized["timezone"],
        "recordedAt": iso_utc(normalized["recorded_at"]),
    }

    if normalized.get("topic"):
        transformed["topic"] = normalized["topic"]

    run_metadata.record_location(normalized["recorded_at"])
    return transformed


def transform_device_status(normalized: dict, device: str, schema: dict) -> dict:
    transformed = {
        "id": str(uuid.uuid4()),
        "entityType": "deviceStatus",
        "version": run_metadata.schemas["deviceStatus"],
        "deviceId": device,
        "battery": normalized["battery"],
        "recordedAt": iso_utc(normalized["recorded_at"]),
    }

    if normalized.get("wifiSSID"):
        transformed["wifiSSID"] = normalized["wifiSSID"]

    if normalized.get("batteryStatus") is not None:
        transformed["batteryStatus"] = normalized["batteryStatus"]

    if normalized.get("connectionStatus"):
        transformed["connectionStatus"] = normalized["connectionStatus"]

    run_metadata.record_device_status(normalized["recorded_at"])
    return transformed


def transform_device(device: str, schema: dict):
    transformed_device = {
        "id": device,
        "entityType": "device",
        "source": "legacy_locations",
        "version": run_metadata.schemas["device"],
    }
    try:
        jsonschema.validate(
            instance=transformed_device, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    run_metadata.record_device()
    return transformed_device


def main():
    args = parse_transform_args()
    file_name = os.path.join(
        args.out_dir, f"{get_file_name(datetime.now(timezone.utc))}")
    canon_file = f"{file_name}.jsonl.gz"
    metadata_file = f"{file_name}.meta.json"

    settings = TransformerEnvVars()

    location_schema = load_schema(
        local=settings.local_loc_schema, default_url=LOCATION_SCHEMA_URL)
    device_schema = load_schema(
        local=settings.local_dev_schema, default_url=DEVICE_SCHEMA_URL)
    device_status_schema = load_schema(
        local=settings.local_dev_status_schema, default_url=DEVICE_STATUS_SCHEMA_URL)

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)

        writer.write(transform_device(
            device=settings.device, schema=device_schema))

        for row in iter_legacy_rows(args.in_dir):
            normalized = normalize_location(row)

            writer.write(transform_location(
                normalized, device=settings.device, schema=location_schema))
            writer.write(transform_device_status(
                normalized, device=settings.device, schema=device_status_schema))

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(run_metadata.to_dict(), f, indent=2)


if __name__ == "__main__":
    main()
