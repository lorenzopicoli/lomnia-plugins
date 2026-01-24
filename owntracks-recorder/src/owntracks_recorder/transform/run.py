import gzip
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from jsonlines import jsonlines

from owntracks_recorder.config import PLUGIN_NAME
from owntracks_recorder.transform.api import OwntracksLocation, getApiResponses
from owntracks_recorder.transform.mappers.device import transform_device
from owntracks_recorder.transform.mappers.device_status import transform_device_status
from owntracks_recorder.transform.mappers.location import transform_location
from owntracks_recorder.transform.meta import TransformRunMetadata
from owntracks_recorder.transform.schemas import Schemas


@dataclass
class TransformerParams:
    device: str
    schemas: Schemas
    metadata: TransformRunMetadata
    data: OwntracksLocation


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))


def run_transform(
    *,
    device: str,
    out_dir: Path,
    in_dir: Path,
    schemas: Schemas,
):
    file_name = f"{PLUGIN_NAME}_canon_{timestamp(datetime.now(timezone.utc))}_{str(uuid.uuid4()).split('-')[0]}"
    file_path = os.path.join(out_dir, file_name)
    canon_file = f"{file_path}.jsonl.gz"
    metadata_file = f"{file_path}.meta.json"

    is_device_saved = False

    metadata = TransformRunMetadata()

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)
        for response in getApiResponses(in_dir, metadata):
            for location in response.data:
                params = TransformerParams(device=device, schemas=schemas, metadata=metadata, data=location)
                if not is_device_saved:
                    # Currently only support one user/device
                    writer.write(transform_device(params))

                writer.write(transform_location(params))
                writer.write(transform_device_status(params))
    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)
