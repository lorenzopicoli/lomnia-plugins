import argparse
import json
import os
from pathlib import Path
from typing import NamedTuple, Optional

import httpx
from pydantic.dataclasses import dataclass


@dataclass
class TransformerEnvVars:
    local_loc_schema: Optional[str] = os.environ["LOCATION_SCHEMA_LOCAL"]
    local_dev_schema: Optional[str] = os.environ["DEVICE_SCHEMA_LOCAL"]
    local_dev_status_schema: Optional[str] = os.environ["DEVICE_STATUS_SCHEMA_LOCAL"]
    device: str = os.environ["DEVICE"]
    skip_schema_check: bool = os.environ.get("SKIP_SCHEMA_CHECK", "").lower() in (
        "1", "true", "yes", "on")


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


LOCATION_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/location.schema.json"
DEVICE_STATUS_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/deviceStatus.schema.json"
DEVICE_SCHEMA_URL = "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/device.schema.json"


class TransformerArgs(NamedTuple):
    in_dir: Path
    out_dir: Path


def parse_transform_args() -> TransformerArgs:
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
