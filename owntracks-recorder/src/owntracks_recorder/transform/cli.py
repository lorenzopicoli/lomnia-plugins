import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.dataclasses import dataclass

from owntracks_recorder.transform.schemas import get_schemas

load_dotenv()


@dataclass
class EnvVars:
    device: str = os.environ["DEVICE"]


def transform():
    parser = argparse.ArgumentParser()

    parser.add_argument("--out_dir", required=True, type=Path, help="Output directory path")
    parser.add_argument("--in_dir", required=True, type=Path, help="Input directory path")
    args = parser.parse_args()

    print(f"In Dir: {args.in_dir}")
    print(f"Out Dir: {args.out_dir}")

    env = EnvVars()
    schemas = get_schemas()


def main():
    transform()


if __name__ == "__main__":
    main()
