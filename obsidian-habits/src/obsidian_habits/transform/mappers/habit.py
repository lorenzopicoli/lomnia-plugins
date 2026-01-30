import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Callable, Optional

import jsonschema

from obsidian_habits.config import PLUGIN_NAME
from obsidian_habits.transform.meta import TransformRunMetadata
from obsidian_habits.transform.schemas import Schemas

FetchTrackerName = Callable[[int], str | None]
FetchTextList = Callable[[int], list[str] | None]


def normalize(value):
    if isinstance(value, Mapping):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def transform_habit(
    *,
    row: dict[str, Any],
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> Optional[dict[str, Any]]:
    value = normalize(row["value"])
    if value == 0 or not value:
        return None
    transformed = {
        "entityType": "habit",
        "version": "1",
        "key": row["key"],
        "value": value,
        "source": PLUGIN_NAME,
        "timezone": row["timezone"],
        "date": row["date"],
        "recordedAt": row["date"],
        # All entries are full days for obsidian
        "isFullDay": True,
    }

    if schemas.habit is not None:
        try:
            jsonschema.validate(instance=transformed, schema=schemas.habit)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise

    metadata.record("habit", datetime.fromisoformat(transformed["recordedAt"]))
    return transformed
