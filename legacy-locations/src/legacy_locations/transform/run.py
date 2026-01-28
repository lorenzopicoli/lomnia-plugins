import gzip
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import jsonlines
from dotenv import load_dotenv

from legacy_locations.config import PLUGIN_NAME
from legacy_locations.transform.mappers.device import transform_device
from legacy_locations.transform.mappers.device_status import transform_device_status
from legacy_locations.transform.mappers.location import transform_location
from legacy_locations.transform.mappers.transformer_params import TransformerParams
from legacy_locations.transform.meta import TransformRunMetadata
from legacy_locations.transform.read_jsonl import get_rows
from legacy_locations.transform.schemas import Schemas

load_dotenv()


def run_transform(device: str, out_dir: str, in_dir: str, schemas: Schemas):
    file_name = f"{PLUGIN_NAME}_canon_{timestamp(datetime.now(timezone.utc))}_{str(uuid.uuid4()).split('-')[0]}"
    file_path = os.path.join(out_dir, file_name)
    canon_file = f"{file_path}.jsonl.gz"
    metadata_file = f"{file_path}.meta.json"

    metadata = TransformRunMetadata()
    metadata.start()
    is_device_saved = False
    log_every = 10000
    row_count = 0

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)

        for row in get_rows(Path(in_dir), metadata):
            row_count += 1
            params = TransformerParams(device=device, schemas=schemas, metadata=metadata, data=row)
            if not is_device_saved:
                # Currently only support one user/device
                writer.write(transform_device(params))
                is_device_saved = True

            writer.write(transform_location(params))
            writer.write(transform_device_status(params))
            if row_count % log_every == 0:
                print(
                    f"Processed {row_count} rows (locations={metadata.counts.get('location')}, device_status={metadata.counts.get('device_status')})"
                )

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
