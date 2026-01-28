import gzip
import json
import sqlite3
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonlines
from dotenv import load_dotenv

from hares.config import PLUGIN_NAME
from hares.transform.mappers.habit import transform_habit
from hares.transform.meta import TransformRunMetadata
from hares.transform.schemas import Schemas

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

    db_path = get_latest_sqlite_file(Path(in_dir))

    if db_path is None:
        print("No SQLite file found in folder")
        return

    metadata.add_files_processed(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    def fetch_tracker_name(tracker_id: int) -> str | None:
        cursor.execute(
            "SELECT name FROM trackers WHERE id = ?",
            (tracker_id,),
        )
        row = cursor.fetchone()
        name = row["name"] if row else None
        return name

    def fetch_text_list(habit_entry_id: int) -> list[str]:
        cursor.execute(
            """
            SELECT name
            FROM text_list_entries
            WHERE entry_id = ?
            ORDER BY rowid
            """,
            (habit_entry_id,),
        )
        texts = [r["name"] for r in cursor.fetchall()]
        return texts

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)

        for row in get_rows(db_path):
            row_count += 1

            transformed = transform_habit(
                row=row,
                schemas=schemas,
                metadata=metadata,
                fetch_tracker_name=fetch_tracker_name,
                fetch_text_list=fetch_text_list,
            )

            writer.write(transformed)

            if row_count % log_every == 0:
                print(f"Processed {row_count} rows (habit={metadata.counts.get('habit', 0)})")

    conn.close()

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def get_latest_sqlite_file(folder: Path) -> Path | None:
    extensions = {".sqlite", ".db", ".sqlite3"}

    sqlite_files = [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in extensions]

    if not sqlite_files:
        return None

    return max(sqlite_files, key=lambda p: p.stat().st_ctime)


def get_rows(db_path: Path) -> Iterator[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM entries
            ORDER BY "createdAt" ASC
            """
        )

        for row in cursor:
            yield dict(row)
    finally:
        conn.close()


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
