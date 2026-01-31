import subprocess
from pathlib import Path


def restore_sqlite_from_gzip_dump(
    dump_gz_path: Path,
    output_sqlite_path: Path,
) -> Path:
    dump_gz_path = dump_gz_path.resolve()
    output_sqlite_path = output_sqlite_path.resolve()

    if not dump_gz_path.exists():
        raise FileNotFoundError(dump_gz_path)

    if output_sqlite_path.exists():
        output_sqlite_path.unlink()

    subprocess.run(  # noqa: S603
        ["sqlite3", str(output_sqlite_path)],  # noqa: S607
        stdin=subprocess.Popen(  # noqa: S603
            ["gzip", "-dc", str(dump_gz_path)],  # noqa: S607
            stdout=subprocess.PIPE,
        ).stdout,
        check=True,
    )

    return output_sqlite_path
