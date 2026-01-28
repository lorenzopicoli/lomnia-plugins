import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

HABIT_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/habit.schema.json"
)


@dataclass
class SchemaEnvVars:
    local_habit_schema: Optional[str] = os.getenv("HABIT_SCHEMA_LOCAL")
    skip_schema_check: bool = os.environ.get("SKIP_SCHEMA_CHECK", "").lower() in ("1", "true", "yes", "on")


class Schemas(NamedTuple):
    habit: Any
    skip_schema_check: bool


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


def get_schemas():
    env = SchemaEnvVars()
    habit_schema = (
        load_schema(local=env.local_habit_schema, default_url=HABIT_SCHEMA_URL) if not env.skip_schema_check else None
    )

    return Schemas(habit_schema, env.skip_schema_check)
