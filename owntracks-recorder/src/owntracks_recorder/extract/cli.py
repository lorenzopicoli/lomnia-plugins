import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv
from pydantic.dataclasses import dataclass

from owntracks_recorder.extract.run import ExtractionParams, run_extract

load_dotenv()


@dataclass
class EnvVars:
    user: str = os.environ["OWNTRACKS_USER"]
    device: str = os.environ["OWNTRACKS_DEVICE"]
    server_url: str = os.environ["OWNTRACKS_URL"]


class ExtractorArgs(NamedTuple):
    start_date: datetime
    out_dir: Path


def extract():
    env = EnvVars()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_date",
        required=True,
        type=lambda value: datetime.fromtimestamp(float(value), tz=timezone.utc),
        help="Start date in YYYY-MM-DD format",
    )

    parser.add_argument("--out_dir", required=True, type=Path, help="Output directory path")

    args = parser.parse_args()
    print("Start date:", args.start_date)
    print("Output dir:", args.out_dir)
    params = ExtractionParams(
        user=env.user, device=env.device, server_url=env.server_url, start_date=args.start_date, out_dir=args.out_dir
    )
    run_extract(params)


def main():
    extract()


if __name__ == "__main__":
    main()
