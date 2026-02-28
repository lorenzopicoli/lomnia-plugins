import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

SLEEP_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/sleep.schema.json"
)
SLEEP_STAGE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/sleep_stage.schema.json"
)
HEART_RATE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/heart_rate.schema.json"
)
DEVICE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/device.schema.json"
)


@dataclass
class SchemaEnvVars:
    local_sleep_schema: Optional[str] = os.getenv("SLEEP_SCHEMA_LOCAL")
    local_sleep_stage_schema: Optional[str] = os.getenv("SLEEP_STAGE_SCHEMA_LOCAL")
    local_heart_rate_schema: Optional[str] = os.getenv("HEART_RATE_SCHEMA_LOCAL")
    local_dev_schema: Optional[str] = os.getenv("DEVICE_SCHEMA_LOCAL")
    skip_schema_check: bool = os.environ.get("SKIP_SCHEMA_CHECK", "").lower() in ("1", "true", "yes", "on")


class Schemas(NamedTuple):
    sleep: Any
    sleep_stage: Any
    heart_rate: Any
    device: Any
    skip_schema_check: bool


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


def get_schemas():
    env = SchemaEnvVars()
    sleep_schema = (
        load_schema(local=env.local_sleep_schema, default_url=SLEEP_SCHEMA_URL) if not env.skip_schema_check else None
    )
    sleep_stage_schema = (
        load_schema(local=env.local_sleep_stage_schema, default_url=SLEEP_STAGE_SCHEMA_URL)
        if not env.skip_schema_check
        else None
    )
    heart_rate_schema = (
        load_schema(local=env.local_heart_rate_schema, default_url=HEART_RATE_SCHEMA_URL)
        if not env.skip_schema_check
        else None
    )
    device_schema = (
        load_schema(local=env.local_dev_schema, default_url=DEVICE_SCHEMA_URL) if not env.skip_schema_check else None
    )

    return Schemas(sleep_schema, sleep_stage_schema, heart_rate_schema, device_schema, env.skip_schema_check)
