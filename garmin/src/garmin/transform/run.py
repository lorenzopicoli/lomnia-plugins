import gzip
import json
import os
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import jsonlines
from dotenv import load_dotenv

from garmin.config import ACTIVITY_FOLDER, HR_FOLDER, PLUGIN_NAME, SLEEP_FOLDER, WEIGHT_FOLDER
from garmin.transform.mappers.hr import transform_hr
from garmin.transform.mappers.sleep import transform_sleep
from garmin.transform.mappers.sleep_stage import transform_sleep_stage
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.hr import HeartRate
from garmin.transform.models.sleep import Sleep
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

    with tempfile.TemporaryDirectory() as tmp_dir, gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)
        tmp_path = Path(tmp_dir)

        for archive in Path(in_dir).glob("*.tar.gz"):
            print("Found archive", archive)
            with tarfile.open(archive, "r:gz") as tar:
                # Unsafe, but I trust the tar :)
                tar.extractall(path=tmp_path)  # noqa: S202
            transformed = process_sleep_files(tmp_path, metadata, schemas)
            for line in transformed:
                writer.write(line)
            transformed = process_hr_files(tmp_path, metadata, schemas)
            for line in transformed:
                writer.write(line)
            # transformed =process_weight_files(tmp_path)
            # writer.write(transformed)
            # transformed =process_activity_files(tmp_path)
            # writer.write(transformed)
    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def process_sleep_files(tmp_path: Path, metadata: TransformRunMetadata, schemas: Schemas):
    result = []
    for sleep_file in (Path(tmp_path) / SLEEP_FOLDER).glob("*.json"):
        raw = json.loads(Path(sleep_file).read_text())
        sleep = Sleep(**raw)
        result.append(transform_sleep(sleep=sleep, metadata=metadata, schemas=schemas))
        result.extend(transform_sleep_stage(sleep=sleep, metadata=metadata, schemas=schemas))
    return result


def process_hr_files(tmp_path: Path, metadata: TransformRunMetadata, schemas: Schemas):
    result = []
    for hr in (Path(tmp_path) / HR_FOLDER).glob("*.json"):
        raw = json.loads(Path(hr).read_text())
        hr = HeartRate(**raw)
        result.append(transform_hr(hr=hr, metadata=metadata, schemas=schemas))
    return result


def process_weight_files(tmp_path: Path):
    for weight in (Path(tmp_path) / WEIGHT_FOLDER).glob("*.json"):
        print("Found weight file", weight)


def process_activity_files(tmp_path: Path):
    for activity in (Path(tmp_path) / ACTIVITY_FOLDER).glob("*.fit"):
        print("Found activity file", activity)


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
