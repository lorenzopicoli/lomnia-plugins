from datetime import datetime
from typing import Any

import jsonschema
from timezonefinder import TimezoneFinder

from garmin.config import PLUGIN_NAME
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.parsers.activity import FITResult
from garmin.transform.schemas import Schemas

tf = TimezoneFinder(in_memory=True)


def transform_location(
    *,
    fit: FITResult,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for record in fit.records:
        timestamp = record.timestamp
        lat = record.lat
        lng = record.lng
        if timestamp is None or lat is None or lng is None:
            continue
        tz = tf.timezone_at(lng=lng, lat=lat)
        transformed: dict[str, Any] = {
            "entityType": "location",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "recordedAt": timestamp.timestamp(),
            "deviceId": fit.device_id,
            "location": {"lat": lat, "lng": lng},
            "timezone": tz,
            "altitude": record.altitude,
            "velocity": record.speed,
        }

        if schemas.location is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.location)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "location",
            [datetime.fromisoformat(transformed["recordedAt"])],
        )
        entries.append(transformed)

    return entries
