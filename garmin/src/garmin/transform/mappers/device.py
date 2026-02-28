from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.device import Device
from garmin.transform.schemas import Schemas


def transform_device(
    *,
    device: Device,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for registered_device in device.RegisteredDevices:
        transformed: dict[str, Any] = {
            "id": str(registered_device.deviceId),
            "name": registered_device.deviceTypeSimpleName,
            "entityType": "device",
            "source": PLUGIN_NAME,
            "version": "1",
        }

        if schemas.device is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.device)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record("device", [])
        entries.append(transformed)
    return entries
