from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.parsers.activity import FITResult
from garmin.transform.schemas import Schemas


def transform_exercise(
    *,
    fit: FITResult,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for session in fit.sessions:
        timestamp = session.timestamp
        if timestamp is None:
            continue

        exercise_type = (
            session.sub_sport if session.sport != "training" and session.sport != "generic" else session.sport
        )
        transformed: dict[str, Any] = {
            "entityType": "exercise",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "recordedAt": timestamp.timestamp(),
            "deviceId": fit.device_id,
            "started_at": session.start_time,
            "ended_at": session.end_time,
            "type": exercise_type,
        }

        if schemas.exercise is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.exercise)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "exercise",
            [datetime.fromisoformat(transformed["recordedAt"])],
        )
        entries.append(transformed)

    return entries
