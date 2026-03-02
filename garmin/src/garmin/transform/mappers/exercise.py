from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.iso_utc import iso_utc
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
        if timestamp is None or session.start_time is None or session.end_time is None:
            print("Skipping session for not having a timezone or start/end date", fit.activity_name)
            continue

        exercise_type = (
            session.sub_sport if session.sport == "training" or session.sport == "generic" else session.sport
        )
        transformed: dict[str, Any] = {
            "entityType": "exercise",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "deviceId": str(fit.device_id),
            "name": fit.activity_name,
            "startedAt": iso_utc(session.start_time),
            "endedAt": iso_utc(session.end_time),
            "exerciseType": exercise_type,
        }

        if schemas.exercise is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.exercise)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "exercise",
            [datetime.fromisoformat(transformed["startedAt"]), datetime.fromisoformat(transformed["endedAt"])],
        )
        entries.append(transformed)

    return entries
