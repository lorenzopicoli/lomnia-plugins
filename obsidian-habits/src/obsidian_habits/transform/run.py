import gzip
import json
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonlines
from dotenv import load_dotenv

from obsidian_habits.config import PLUGIN_NAME
from obsidian_habits.transform.mappers.habit import transform_habit
from obsidian_habits.transform.meta import TransformRunMetadata
from obsidian_habits.transform.schemas import Schemas

load_dotenv()


def run_transform(out_dir: str, in_dir: str, schemas: Schemas):
    file_name = f"{PLUGIN_NAME}_canon_{timestamp(datetime.now(timezone.utc))}_{str(uuid.uuid4()).split('-')[0]}"
    file_path = Path(out_dir) / file_name
    canon_file = f"{file_path}.jsonl.gz"
    metadata_file = f"{file_path}.meta.json"

    metadata = TransformRunMetadata()
    metadata.start()
    log_every = 10_000
    row_count = 0

    json_path = get_latest_json_file(Path(in_dir))

    if json_path is None:
        print("No json file found in folder")
        return

    metadata.add_files_processed(json_path)

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)

        for row in get_rows(json_path):
            row_count += 1

            transformed = transform_habit(
                row=row,
                schemas=schemas,
                metadata=metadata,
            )

            if transformed:
                writer.write(transformed)

            if row_count % log_every == 0:
                print(f"Processed {row_count} rows (habit={metadata.counts.get('habit', 0)})")

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def get_latest_json_file(folder: Path) -> Path | None:
    extensions = {".json"}
    exclude_suffixes = {".meta.json"}

    files = [
        path
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in extensions
        and not path.name.lower().endswith(tuple(exclude_suffixes))
    ]
    if not files:
        return None

    return max(files, key=lambda p: p.stat().st_ctime)


def get_rows(json_path: Path) -> Iterator[dict[str, Any]]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise TypeError("JSON_MISSING_ARRAY")

    yield from data


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
