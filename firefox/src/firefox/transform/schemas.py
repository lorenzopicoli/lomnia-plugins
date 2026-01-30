import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

WEBSITE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/website.schema.json"
)
WEBSITE_VISIT_SCHEMA_URL = (
    "https://raw.githubusercontent.com/lorenzopicoli/lomnia/refs/heads/main/backend/schemas/website_visit.schema.json"
)


@dataclass
class SchemaEnvVars:
    local_website_schema: Optional[str] = os.getenv("WEBSITE_SCHEMA_LOCAL")
    local_website_visit_schema: Optional[str] = os.getenv("WEBSITE_VISIT_SCHEMA_LOCAL")
    skip_schema_check: bool = os.environ.get("SKIP_SCHEMA_CHECK", "").lower() in ("1", "true", "yes", "on")


class Schemas(NamedTuple):
    website: Any
    website_visit: Any
    skip_schema_check: bool


def load_schema(local: str | None, default_url: str):
    if local:
        file_path = Path(local)
        if file_path.exists():
            return json.loads(file_path.read_text())

    return httpx.get(default_url).json()


def get_schemas():
    env = SchemaEnvVars()
    website_schema = (
        load_schema(local=env.local_website_schema, default_url=WEBSITE_SCHEMA_URL)
        if not env.skip_schema_check
        else None
    )
    website_visit_schema = (
        load_schema(local=env.local_website_visit_schema, default_url=WEBSITE_VISIT_SCHEMA_URL)
        if not env.skip_schema_check
        else None
    )

    return Schemas(website_schema, website_visit_schema, env.skip_schema_check)
