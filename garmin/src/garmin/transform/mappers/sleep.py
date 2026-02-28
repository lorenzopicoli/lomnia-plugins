from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.get_sleep_id import get_sleep_id
from garmin.transform.mappers.utils.to_utc_iso_from_epoch import to_utc_iso_from_epoch
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.sleep import Sleep
from garmin.transform.schemas import Schemas


def transform_sleep(
    *,
    sleep: Sleep,
    deviceId: str,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> dict[str, Any]:
    dto = sleep.dailySleepDTO

    started_at = to_utc_iso_from_epoch(dto.sleepStartTimestampGMT)
    ended_at = to_utc_iso_from_epoch(dto.sleepEndTimestampGMT)

    transformed: dict[str, Any] = {
        "entityType": "sleep",
        "version": "1",
        "id": get_sleep_id(sleep),
        "source": PLUGIN_NAME,
        "startedAt": started_at,
        "endedAt": ended_at,
        "automaticScore": dto.sleepScores.overall.value,
        "deviceId": deviceId,
    }

    if schemas.sleep is not None:
        try:
            jsonschema.validate(instance=transformed, schema=schemas.sleep)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise

    metadata.record(
        "sleep", [datetime.fromisoformat(transformed["startedAt"]), datetime.fromisoformat(transformed["endedAt"])]
    )
    return transformed
