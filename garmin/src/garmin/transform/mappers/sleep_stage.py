import hashlib
from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.get_sleep_id import get_sleep_id
from garmin.transform.mappers.utils.iso_utc import iso_utc
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.sleep import Sleep
from garmin.transform.schemas import Schemas


def hash_interval(started_at: str, ended_at: str) -> str:
    raw = f"{started_at}|{ended_at}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def transform_sleep_stage(
    *,
    sleep: Sleep,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    levels = sleep.sleepLevels
    result = []
    for level in levels:
        start = level.startGMT
        end = level.endGMT
        stage = level.activityLevel

        started_at = iso_utc(start)
        ended_at = iso_utc(end)

        transformed: dict[str, Any] = {
            "id": f"{get_sleep_id(sleep)}_{hash_interval(started_at, ended_at)}",
            "entityType": "sleep_stage",
            "version": "1",
            "source": PLUGIN_NAME,
            "startedAt": started_at,
            "endedAt": ended_at,
            "type": stage,
            "sleepId": get_sleep_id(sleep),
            # For me it's safe to take that since i only have a watch
            "deviceId": str(sleep.wellnessSpO2SleepSummaryDTO.deviceId),
        }

        if schemas.sleep_stage is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.sleep_stage)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "sleep_stage",
            [datetime.fromisoformat(transformed["startedAt"]), datetime.fromisoformat(transformed["endedAt"])],
        )
        result.append(transformed)
    return result
