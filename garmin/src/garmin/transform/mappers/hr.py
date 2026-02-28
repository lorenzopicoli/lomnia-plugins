from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.to_utc_iso_from_epoch import to_utc_iso_from_epoch
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.hr import HeartRate
from garmin.transform.schemas import Schemas


def transform_hr(
    *,
    hr: HeartRate,
    deviceId: str,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for _i, row in enumerate(hr.heartRateValues):
        if not row or len(row) < 2:
            continue

        timestamp_ms, bpm = row

        if bpm is None:
            continue

        if timestamp_ms is None:
            raise
        timestamp = to_utc_iso_from_epoch(timestamp_ms)

        transformed: dict[str, Any] = {
            "entityType": "heartRate",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp_ms}",
            "source": PLUGIN_NAME,
            "recordedAt": timestamp,
            "heartRate": bpm,
            "deviceId": deviceId,
        }
        if schemas.heart_rate is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.heart_rate)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "heart_rate",
            [datetime.fromisoformat(transformed["recordedAt"])],
        )
        entries.append(transformed)

    return entries
