import argparse
import json
from pathlib import Path
from typing import NamedTuple

import httpx

from owntracks_recorder.owntracks_location import OwntracksLocationApiResponse

SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia-ingester/refs/heads/main/src/json_schemas/v1/Location.schema.json"

schema = httpx.get(SCHEMA_URL).json()


class TransformerArgs(NamedTuple):
    in_dir: Path
    out_dir: Path


def parse_args() -> TransformerArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--out_dir",
        required=True,
        type=Path,
        help="Output directory path"
    )

    parser.add_argument(
        "--in_dir",
        required=True,
        type=Path,
        help="Input directory path"
    )

    parsed = parser.parse_args()
    return TransformerArgs(in_dir=parsed.in_dir, out_dir=parsed.out_dir)


def transform():
    args = parse_args()
    print("Input dir:", args.in_dir)
    print("Output dir:", args.out_dir)
    for path in args.in_dir.iterdir():
        if path.is_file():
            print(f"\n--- {path.name} ---")
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                model = OwntracksLocationApiResponse(**data)
                print(model.count)


if __name__ == "__main__":
    print(transform())
