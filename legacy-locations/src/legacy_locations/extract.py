import argparse
import json
import shutil
import uuid
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

PACKAGE_NAME = "legacy_locations"

_ = load_dotenv()


class ExtractorArgs(NamedTuple):
    start_date: datetime
    out_dir: Path
    in_dir: Path


class MissingEnvVar(ValueError):
    def __init__(self, value: str):
        super().__init__(f"Missing env var: {value}")


def get_short_uid() -> str:
    return str(uuid.uuid4()).split("-")[0]


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"


def write_meta_file(
    *,
    out_dir: Path,
    source_path: Path,
    copied_path: Path,
    extract_start: datetime,
) -> Path:
    meta = {
        "extractor_version": get_version(),
        "extractor": PACKAGE_NAME,
        "extract_start": extract_start.isoformat(),
        "extract_end": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_path),
    }
    meta_path = out_dir / f"{copied_path.name}.meta.json"
    _ = meta_path.write_text(json.dumps(meta, indent=2))

    return meta_path


def parse_extract_args() -> ExtractorArgs:
    parser = argparse.ArgumentParser()

    _ = parser.add_argument(
        "--start_date",
        required=True,
        type=lambda value: datetime.fromtimestamp(float(value), tz=timezone.utc),
        help="Start date in POSIX timestamp (UTC)",
    )

    _ = parser.add_argument(
        "--out_dir",
        required=True,
        type=Path,
        help="Output directory path",
    )

    _ = parser.add_argument(
        "--in_dir",
        required=True,
        type=Path,
        help="Input directory path",
    )

    args = parser.parse_args()

    return ExtractorArgs(start_date=args.start_date, out_dir=args.out_dir, in_dir=args.in_dir)


def extract():
    args = parse_extract_args()

    print("Start date:", args.start_date)
    print("Input dir:", args.in_dir)
    print("Output dir:", args.out_dir)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    extract_start = datetime.now(timezone.utc)
    copied = 0

    for path in Path(args.in_dir).rglob("*"):
        if not path.is_file():
            continue

        # Check if file was created or modified after the start date. Should be safe to remove since effectively
        # we just want to extract everything in the folder
        # mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        # if mtime <= args.start_date:
        #     continue

        suffix = "".join(path.suffixes)
        base = path.name.removesuffix(suffix)

        dest_name = f"{base}_{get_short_uid()}{suffix}"
        dest_path = args.out_dir / dest_name

        _ = shutil.copy2(path, dest_path)

        _ = write_meta_file(
            out_dir=args.out_dir,
            source_path=path,
            copied_path=dest_path,
            extract_start=extract_start,
        )

        copied += 1

    print(f"Copied {copied} file(s)")


def main():
    extract()


if __name__ == "__main__":
    main()
