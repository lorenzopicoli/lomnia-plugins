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
