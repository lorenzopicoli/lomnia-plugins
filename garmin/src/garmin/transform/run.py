import json
import os
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from garmin.config import ACTIVITY_FOLDER, HR_FOLDER, PLUGIN_NAME, SLEEP_FOLDER, WEIGHT_FOLDER
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.schemas import Schemas

load_dotenv()


def run_transform(out_dir: str, in_dir: str, schemas: Schemas):
    file_name = f"{PLUGIN_NAME}_canon_{timestamp(datetime.now(timezone.utc))}_{str(uuid.uuid4()).split('-')[0]}"
    file_path = os.path.join(out_dir, file_name)
    canon_file = f"{file_path}.jsonl.gz"
    metadata_file = f"{file_path}.meta.json"

    metadata = TransformRunMetadata()
    metadata.start()
    # log_every = 10000
    # row_count = 0

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        for archive in Path(in_dir).glob("*.tar.gz"):
            print("found archive", archive)
            with tarfile.open(archive, "r:gz") as tar:
                # Unsafe, but I trust the tar :)
                tar.extractall(path=tmp_path)  # noqa: S202

        for sleep_file in (Path(tmp_path) / SLEEP_FOLDER).glob("*.json"):
            print("Found sleep file", sleep_file)
        for weight in (Path(tmp_path) / WEIGHT_FOLDER).glob("*.json"):
            print("Found weight file", weight)
        for hr in (Path(tmp_path) / HR_FOLDER).glob("*.json"):
            print("Found hr file", hr)
        for activity in (Path(tmp_path) / ACTIVITY_FOLDER).glob("*.fit"):
            print("Found activit file", activity)

        # writer = jsonlines.Writer(gz)
        # Example bellow of iterating over a file and writting results and logging progress
        # for row in get_rows(Path(in_dir), metadata):
        #     row_count += 1
        #     params = TransformerParams(device=device, schemas=schemas, metadata=metadata, data=row)
        #
        #     writer.write(transform_location(params))
        #     writer.write(transform_device_status(params))
        #     if row_count % log_every == 0:
        #       print(
        #          f"Processed {row_count} rows (locations={metadata.counts.get('location')}, device_status={metadata.counts.get('device_status')})"
        #       )

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
