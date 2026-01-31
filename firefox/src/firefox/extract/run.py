import gzip
import shutil
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from firefox.extract.meta import write_meta_file


@dataclass
class ExtractionParams:
    start_date: datetime
    out_dir: Path
    in_dir: Path


def run_extract(params: ExtractionParams):
    extract_start = datetime.now(timezone.utc)

    # Example: read all files in a folder and copy them as they are to the out_dir
    for path in Path(params.in_dir).rglob("*"):
        if not path.is_file():
            continue

        suffix = "".join(path.suffixes)
        base = path.name.removesuffix(suffix)

        file_name = f"{base}_{str(uuid.uuid4()).split('-')[0]}"
        dest_path = params.out_dir / f"{file_name}.sql.gz"
        #     "~/.mozilla/firefox/",
        #     "~/.var/app/org.mozilla.firefox/.mozilla/firefox/",
        #     "~/snap/firefox/common/.mozilla/firefox/",
        #     "~/Library/Application Support/Firefox/Profiles/",

        earliest, latest = gzip_sqlite_dump(path, dest_path)

        write_meta_file(
            out_dir=params.out_dir,
            source_path=path,
            file_name=file_name,
            extract_start=extract_start,
            data_window_start=earliest,
            data_window_end=latest,
        )

        print(f"Copied file {path}")


def _moz_timestamp_to_iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc).isoformat()


# It seems like it's better to VACUMN, dump and compress the DB rather than just compressing
# the db file
def gzip_sqlite_dump(sqlite_path: Path, output_path: Path | None = None) -> tuple[str | None, str | None]:
    sqlite_path = sqlite_path.resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(sqlite_path)

    if output_path is None:
        output_path = sqlite_path.with_suffix(".sql.gz")
    output_path = Path(output_path).resolve()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tmp_db = tmpdir / sqlite_path.name

        shutil.copy2(sqlite_path, tmp_db)

        conn = sqlite3.connect(tmp_db)
        try:
            conn.execute("VACUUM;")
            row = conn.execute(
                """
                SELECT
                    MIN(visit_date) AS earliest,
                    MAX(visit_date) AS latest
                FROM moz_historyvisits
                """
            ).fetchone()

            earliest, latest = row
            earliest = _moz_timestamp_to_iso(earliest)
            latest = _moz_timestamp_to_iso(latest)
            print("Firefox history range:")
            print("  earliest:", earliest)
            print("  latest:  ", latest)
        finally:
            conn.close()

        conn = sqlite3.connect(tmp_db)
        try:
            with gzip.open(output_path, "wt", encoding="utf-8") as gz:
                for line in conn.iterdump():
                    gz.write(line)
                    gz.write("\n")
        finally:
            conn.close()

    return earliest, latest
