import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import jsonlines
from dotenv import load_dotenv

from legacy_locations.transform.helpers import get_file_name
from legacy_locations.transform.normalize import normalize_row
from legacy_locations.transform.transform import transform_device, transform_device_status, transform_location
from legacy_locations.transform.transformer_config import (
    DEVICE_SCHEMA_URL,
    DEVICE_STATUS_SCHEMA_URL,
    LOCATION_SCHEMA_URL,
    TransformerEnvVars,
    load_schema,
    parse_transform_args,
)
from legacy_locations.transform.transformer_run_metadata import TransformRunMetadata

load_dotenv()


def is_owntracks_raw(raw: dict) -> bool:
    return "lat" in raw and "lon" in raw and "tst" in raw


class FailedToTransform(ValueError):
    def __init__(self, value):
        super().__init__(value)


def iter_legacy_rows(in_dir: Path, run_metadata: TransformRunMetadata):
    for path in in_dir.iterdir():
        if path.is_file() and ".jsonl" in path.suffixes and ".gz" in path.suffixes and ".meta" not in path.suffixes:
            run_metadata.add_input(path)
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for line in f:
                    yield json.loads(line)


def main():
    args = parse_transform_args()
    file_name = os.path.join(args.out_dir, f"{get_file_name(datetime.now(timezone.utc))}")
    canon_file = f"{file_name}.jsonl.gz"
    metadata_file = f"{file_name}.meta.json"

    settings = TransformerEnvVars()
    run_metadata = TransformRunMetadata()
    run_metadata.start()

    run_metadata.set_schema(entity="location", version="1")
    run_metadata.set_schema(entity="device", version="1")
    run_metadata.set_schema(entity="deviceStatus", version="1")

    location_schema = (
        load_schema(local=settings.local_loc_schema, default_url=LOCATION_SCHEMA_URL)
        if not settings.skip_schema_check
        else None
    )
    device_schema = (
        load_schema(local=settings.local_dev_schema, default_url=DEVICE_SCHEMA_URL)
        if not settings.skip_schema_check
        else None
    )
    device_status_schema = (
        load_schema(local=settings.local_dev_status_schema, default_url=DEVICE_STATUS_SCHEMA_URL)
        if not settings.skip_schema_check
        else None
    )

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)

        writer.write(transform_device(device=settings.device, schema=device_schema, run_metadata=run_metadata))

        for row in iter_legacy_rows(args.in_dir, run_metadata):
            normalized = normalize_row(row)

            writer.write(
                transform_location(
                    normalized, device=settings.device, schema=location_schema, run_metadata=run_metadata
                )
            )
            writer.write(
                transform_device_status(
                    normalized, device=settings.device, schema=device_status_schema, run_metadata=run_metadata
                )
            )

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(run_metadata.to_dict(), f, indent=2)


if __name__ == "__main__":
    main()
