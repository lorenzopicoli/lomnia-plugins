import gzip
import sqlite3
from pathlib import Path


def restore_sqlite_from_gzip_dump(
    dump_gz_path: Path,
    output_sqlite_path: Path,
) -> Path:
    dump_gz_path = Path(dump_gz_path).resolve()
    output_sqlite_path = Path(output_sqlite_path).resolve()

    if not dump_gz_path.exists():
        raise FileNotFoundError(dump_gz_path)

    if output_sqlite_path.exists():
        output_sqlite_path.unlink()

    conn = sqlite3.connect(output_sqlite_path)
    try:
        conn.executescript(
            """
            PRAGMA journal_mode = OFF;
            PRAGMA synchronous = OFF;
            PRAGMA temp_store = MEMORY;
            """
        )

        with gzip.open(dump_gz_path, "rt", encoding="utf-8") as gz:
            sql_buffer: list[str] = []

            for line in gz:
                sql_buffer.append(line)

                # SQLite dump statements always end with semicolons
                if line.rstrip().endswith(";"):
                    conn.executescript("".join(sql_buffer))
                    sql_buffer.clear()

        conn.commit()
    finally:
        conn.close()

    return output_sqlite_path
