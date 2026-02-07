import sqlite3
from datetime import datetime
from typing import Any, Callable

import jsonschema

from hares.config import PLUGIN_NAME
from hares.transform.mappers.utils.unitx_to_utc_iso import unix_to_utc_iso
from hares.transform.meta import TransformRunMetadata
from hares.transform.schemas import Schemas

FetchTracker = Callable[[int], sqlite3.Row]
FetchTextList = Callable[[int], list[str] | None]


def extract_value(row: dict[str, Any]) -> Any:
    if row.get("numberValue") is not None:
        return row["numberValue"]

    if row.get("booleanValue") is not None:
        return bool(row["booleanValue"])

    return None


def transform_habit(
    *,
    row: dict[str, Any],
    metadata: TransformRunMetadata,
    schemas: Schemas,
    fetch_tracker: FetchTracker,
    fetch_text_list: FetchTextList,
) -> dict[str, Any]:
    tracker = fetch_tracker(row["tracker_id"])
    transformed = {
        "entityType": "habit",
        "version": "1",
        "id": "hares_" + str(row["id"]),
        "key": tracker["name"],
        "date": unix_to_utc_iso(row["date"]),
        "source": PLUGIN_NAME,
        "timezone": row["timezone"],
        "recordedAt": unix_to_utc_iso(row["createdAt"]),
        "isFullDay": False,
    }

    value = extract_value(row)

    if value is None:
        value = fetch_text_list(row["id"])

    transformed["value"] = value

    if tracker["prefix"]:
        transformed["valuePrefix"] = tracker["prefix"]
    if tracker["suffix"]:
        transformed["valueSuffix"] = tracker["suffix"]

    if row.get("comment"):
        transformed["comments"] = row["comment"]

    if row.get("periodOfDay"):
        transformed["periodOfDay"] = row["periodOfDay"]

    if schemas.habit is not None:
        try:
            jsonschema.validate(instance=transformed, schema=schemas.habit)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise

    metadata.record("habit", datetime.fromisoformat(transformed["recordedAt"]))
    return transformed
