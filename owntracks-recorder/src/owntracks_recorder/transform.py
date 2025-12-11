import argparse
import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import httpx
import jsonlines
import jsonschema

from owntracks_recorder.owntracks_location import OwntracksLocation, OwntracksLocationApiResponse, TriggerType

SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia-ingester/refs/heads/main/src/json_schemas/v1/Location.schema.json"
# SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia-ingester/refs/heads/main/src/json_schemas/v1/DeviceStatus.schema.json"

schema = httpx.get(SCHEMA_URL).json()


class TransformerArgs(NamedTuple):
    in_dir: Path
    out_dir: Path


class FailedToTransform(ValueError):
    def __init__(self, value):
        super().__init__(value)


def parse_args() -> TransformerArgs:
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
        if path.is_file():
            print(f"\n--- {path.name} ---")
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                responses.append(OwntracksLocationApiResponse(**data))
    return responses


def transform(response: OwntracksLocation):
    location = response

    canonical = {
        "version": "1",
        "id": location.id,
        # "deviceId": location.
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
        "locationRecordedAt": datetime.fromtimestamp(location.tst, tz=timezone.utc).isoformat()
    }

    if location.t == TriggerType.p:
        canonical["trigger"] = "ping"
    elif location.t == TriggerType.c:
        canonical["trigger"] = "circular"
    elif location.t == TriggerType.r:
        canonical["trigger"] = "report_location"
    elif location.t == TriggerType.u:
        canonical["trigger"] = "manual"
    print(canonical)
    try:
        jsonschema.validate(
            instance=canonical, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    return canonical


if __name__ == "__main__":
    args = parse_args()
    print("Input dir:", args.in_dir)
    print("Output dir:", args.out_dir)
    file_name = os.path.join(
        args.out_dir, "owntracks_canonical.jsonl.gz")
    # with jsonlines.open(file_name, mode='w') as writer:
    with gzip.open(file_name, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)
        for response in getApiResponses(args.in_dir):
            for location in response.data:
                canonical = transform(location)
                writer.write(canonical)
                print("Valid data is valid.")
