from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.iso_utc import iso_utc
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.parsers.activity import FITResult
from garmin.transform.schemas import Schemas


def transform_device_status(
    *,
    fit: FITResult,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for status in fit.device_statuses:
        timestamp = status.timestamp
        if timestamp is None:
            continue

        transformed: dict[str, Any] = {
            "entityType": "deviceStatus",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "recordedAt": iso_utc(timestamp),
            "battery": status.battery_level,
            "temperature": status.temperature,
            "deviceId": str(fit.device_id),
        }

        if schemas.device_status is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.device_status)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "device_status",
            [datetime.fromisoformat(transformed["recordedAt"])],
        )
        entries.append(transformed)

    return entries
