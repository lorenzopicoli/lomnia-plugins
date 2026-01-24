import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

import httpx

LOCATION_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/location.schema.json"
)
DEVICE_STATUS_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/deviceStatus.schema.json"
)
DEVICE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/device.schema.json"
)


@dataclass
class SchemaEnvVars:
    local_loc_schema: Optional[str] = os.getenv("LOCATION_SCHEMA_LOCAL")
    local_dev_schema: Optional[str] = os.getenv("DEVICE_SCHEMA_LOCAL")
    local_dev_status_schema: Optional[str] = os.getenv("DEVICE_STATUS_SCHEMA_LOCAL")
    skip_schema_check: bool = os.environ.get("SKIP_SCHEMA_CHECK", "").lower() in ("1", "true", "yes", "on")


class Schemas(NamedTuple):
    location: Any
    device: Any
    device_status: Any


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


def get_schemas():
    env = SchemaEnvVars()
    location_schema = (
        load_schema(local=env.local_loc_schema, default_url=LOCATION_SCHEMA_URL) if not env.skip_schema_check else None
    )
    device_schema = (
        load_schema(local=env.local_dev_schema, default_url=DEVICE_SCHEMA_URL) if not env.skip_schema_check else None
    )
    device_status_schema = (
        load_schema(local=env.local_dev_status_schema, default_url=DEVICE_STATUS_SCHEMA_URL)
        if not env.skip_schema_check
        else None
    )

    return Schemas(location_schema, device_schema, device_status_schema)
