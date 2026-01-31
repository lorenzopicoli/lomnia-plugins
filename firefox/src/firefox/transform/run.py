import gzip
import json
import os
import sqlite3
import tempfile
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import jsonlines
from dotenv import load_dotenv

from firefox.config import PLUGIN_NAME
from firefox.transform.mappers.transformer_params import WebsiteTransformerParams, WebsiteVisitTransformerParams
from firefox.transform.mappers.visit import transform_website_visit
from firefox.transform.mappers.website import transform_website
from firefox.transform.meta import TransformRunMetadata
from firefox.transform.models import MozHistoryVisit, MozPlace
from firefox.transform.restore_sqlite_from_gzip_dump import restore_sqlite_from_gzip_dump
from firefox.transform.schemas import Schemas

load_dotenv()


def run_transform(out_dir: str, in_dir: str, schemas: Schemas):
    file_name = f"{PLUGIN_NAME}_canon_{timestamp(datetime.now(timezone.utc))}_{str(uuid.uuid4()).split('-')[0]}"
    file_path = os.path.join(out_dir, file_name)
    canon_file = f"{file_path}.jsonl.gz"
    metadata_file = f"{file_path}.meta.json"

    metadata = TransformRunMetadata()
    metadata.start()
    log_every = 10000
    row_count = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        restored_dbs: list[Path] = []
        for dump_path in Path(in_dir).iterdir():
            if dump_path.is_file() and dump_path.name.endswith(".sql.gz"):
                restored_db = tmpdir / dump_path.stem.replace(".sql", "")
                restore_sqlite_from_gzip_dump(dump_path, restored_db)
                restored_dbs.append(restored_db)

        with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
            writer = jsonlines.Writer(gz)

            for db_path in restored_dbs:
                for row in fetch_websites(db_path):
                    row_count += 1
                    params = WebsiteTransformerParams(schemas=schemas, metadata=metadata, place=row)
                    writer.write(transform_website(params))

                    if row_count % log_every == 0:
                        print(
                            f"Processed {row_count} rows "
                            f"(website={metadata.counts.get('website')}, "
                            f"website_visits={metadata.counts.get('website_visit')})"
                        )
                for row in fetch_website_visits(db_path):
                    row_count += 1
                    params = WebsiteVisitTransformerParams(schemas=schemas, metadata=metadata, place=row)
                    writer.write(transform_website_visit(params))

                    if row_count % log_every == 0:
                        print(
                            f"Processed {row_count} rows "
                            f"(website={metadata.counts.get('website')}, "
                            f"website_visits={metadata.counts.get('website_visit')})"
                        )

    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def fetch_websites(db_path: Path) -> Iterator[MozPlace]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("SELECT * FROM moz_places")
        for row in cursor:
            yield MozPlace.model_validate(dict(row))
    finally:
        conn.close()


def fetch_website_visits(db_path: Path) -> Iterator[MozHistoryVisit]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(
            """
            SELECT
                v.*,
                p.guid AS place_guid,
                a.content AS downloaded_file
            FROM moz_historyvisits v
            LEFT JOIN moz_places p
                ON p.id = v.place_id
            LEFT JOIN moz_annos a
                ON a.place_id = v.place_id AND a.anno_attribute_id = 1
            """
        )

        for row in cursor:
            yield MozHistoryVisit.model_validate(dict(row))
    finally:
        conn.close()


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))
