import argparse
import gzip
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple, Optional

import httpx
import jsonlines
import jsonschema
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass

from owntracks_recorder.owntracks_location import OwntracksLocation, OwntracksLocationApiResponse, TriggerType
from owntracks_recorder.transform_run_metadata import TransformRunMetadata

load_dotenv()


@dataclass
class TransformerEnvVars:
    user: str = os.environ["OWNTRACKS_USER"]
    device: str = os.environ["OWNTRACKS_DEVICE"]
    local_loc_schema: Optional[str] = os.environ["LOCATION_SCHEMA_LOCAL"]
    local_dev_schema: Optional[str] = os.environ["DEVICE_SCHEMA_LOCAL"]
    local_dev_status_schema: Optional[str] = os.environ["DEVICE_STATUS_SCHEMA_LOCAL"]


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


run_metadata = TransformRunMetadata()
run_metadata.start()
settings = TransformerEnvVars()


LOCATION_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/location.schema.json"
DEVICE_STATUS_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/deviceStatus.schema.json"
DEVICE_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/device.schema.json"

location_schema = load_schema(
    local=settings.local_loc_schema, default_url=LOCATION_SCHEMA_URL)
device_schema = load_schema(
    local=settings.local_dev_schema, default_url=DEVICE_SCHEMA_URL)
device_status_schema = load_schema(
    local=settings.local_dev_status_schema, default_url=DEVICE_STATUS_SCHEMA_URL)

run_metadata.set_schema(
    entity="location", version="1")
run_metadata.set_schema(
    entity="device", version="1")
run_metadata.set_schema(
    entity="deviceStatus", version="1")


def iso_utc(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class MissingEnvVar(ValueError):
    def __init__(self, value):
        self.value = value
        message = f"Missing env var: {value}"
        super().__init__(message)


class TransformerArgs(NamedTuple):
    in_dir: Path
    out_dir: Path


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


def getApiResponses(in_dir: Path):
    responses: list[OwntracksLocationApiResponse] = []
    for path in in_dir.iterdir():
        if path.is_file() and path.suffix == ".gz":
            print(f"\n--- {path.name} ---")
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
                run_metadata.add_input(path)
                responses.append(OwntracksLocationApiResponse(**data))
    return responses


def get_trigger(location: OwntracksLocation) -> str | None:
    mapping = {
        TriggerType.p: "ping",
        TriggerType.c: "circular",
        TriggerType.r: "report_location",
        TriggerType.u: "manual",
    }
    if location.t is None:
        return None
    return mapping.get(location.t)


def get_batt_status(location: OwntracksLocation) -> str | None:
    mapping = {
        0: "unknown",
        1: "unplugged",
        2: "charging",
        3: "full",
    }
    if location.batt is None:
        return None
    return mapping.get(location.batt, None)


def get_conn_status(location: OwntracksLocation) -> str | None:
    mapping = {
        "w": "wifi",
        "o": "offline",
        "m": "data",
    }
    if location.conn is None:
        return None
    return mapping.get(location.conn, None)


def transform_device_status(response: OwntracksLocation):
    device = os.environ.get('OWNTRACKS_DEVICE', None)
    if device is None:
        raise MissingEnvVar("OWNTRACKS_DEVICE")
    location = response
    recorded_at: datetime = datetime.fromtimestamp(
        location.tst, tz=timezone.utc)
    transformed_device_status = {
        "id": location.id,
        "entityType": "deviceStatus",
        "source": "owntracks",
        "version": run_metadata.schemas["deviceStatus"],
        "deviceId": device,
        "battery": location.batt,
        "timezone": location.tzname,
        "recordedAt": iso_utc(recorded_at)
    }

    if (location.SSID is not None):
        transformed_device_status["wifiSSID"] = location.SSID
    if (trigger := get_trigger(location)):
        transformed_device_status["trigger"] = trigger
    if (batt_status := get_batt_status(location)):
        transformed_device_status["batteryStatus"] = batt_status
    if (conn_status := get_conn_status(location)):
        transformed_device_status["connectionStatus"] = conn_status

    try:
        jsonschema.validate(
            instance=transformed_device_status, schema=device_status_schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    run_metadata.record_device_status(recorded_at)
    return transformed_device_status


def transform_device():
    device = os.environ.get('OWNTRACKS_DEVICE', None)
    if device is None:
        raise MissingEnvVar("OWNTRACKS_DEVICE")
    transformed_device = {
        "id": device,
        "entityType": "device",
        "source": "owntracks",
        "version": run_metadata.schemas["device"],
    }
    try:
        jsonschema.validate(
            instance=transformed_device, schema=device_schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    run_metadata.record_device()
    return transformed_device


def transform_location(response: OwntracksLocation):
    location = response
    # Only support single device for now
    device = os.environ.get('OWNTRACKS_DEVICE', None)
    if device is None:
        raise MissingEnvVar("OWNTRACKS_DEVICE")

    recorded_at: datetime = datetime.fromtimestamp(
        location.tst, tz=timezone.utc)
    transformed_loc = {
        "version": run_metadata.schemas["location"],
        "id": location.id,
        "entityType": "location",
        "deviceId": device,
        "source": "owntracks",
        "gpsSource": location.source,
        "accuracy": location.acc,
        "verticalAccuracy": location.vac,
        "velocity": location.vel,
        "altitude": location.alt,
        "location": {
            "lat": location.lat,
            "lng": location.lon
        },
        "topic": location.topic,
        "timezone": location.tzname,
        "recordedAt": iso_utc(recorded_at)
    }

    trigger = get_trigger(location)
    if trigger:
        transformed_loc["trigger"] = "ping"

    try:
        jsonschema.validate(
            instance=transformed_loc, schema=location_schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    run_metadata.record_location(recorded_at)
    return transformed_loc


def timestamp_for_file_name(time: datetime) -> str:
    return str(int(time.timestamp()))


def get_short_uid() -> str:
    return str(uuid.uuid4()).split("-")[0]


def get_file_name(date: datetime) -> str:
    service = "owntracks"
    return f"{service}_canon_{timestamp_for_file_name(date)}_{get_short_uid()}"


def main():
    args = parse_transform_args()
    file_name = os.path.join(
        args.out_dir, f"{get_file_name(datetime.now(timezone.utc))}")
    canon_file = f"{file_name}.jsonl.gz"
    metadata_file = f"{file_name}.meta.json"

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)
        # Currently only support one user/device
        writer.write(transform_device())
        for response in getApiResponses(args.in_dir):
            for location in response.data:
                writer.write(transform_location(location))
                writer.write(transform_device_status(location))
    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(run_metadata.to_dict(), f, indent=2)


if __name__ == "__main__":
    main()
