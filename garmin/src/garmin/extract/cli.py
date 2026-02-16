import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

from garmin.extract.run import ExtractionParams, run_extract

load_dotenv()


class ExtractorArgs(NamedTuple):
    start_date: datetime
    out_dir: Path
    in_dir: Path


def parse_extract_args() -> ExtractorArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_date",
        required=True,
        type=lambda value: datetime.fromtimestamp(float(value), tz=timezone.utc),
        help="Start date in POSIX timestamp (UTC)",
    )

    parser.add_argument(
        "--out_dir",
        required=True,
        type=Path,
        help="Output directory path",
    )

    parser.add_argument(
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

    params = ExtractionParams(start_date=args.start_date, out_dir=args.out_dir, in_dir=args.in_dir)
    run_extract(params)


def main():
    extract()


if __name__ == "__main__":
    main()
