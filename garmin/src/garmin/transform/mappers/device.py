from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.models.device import Device
from garmin.transform.parsers.activity import FITResult
from garmin.transform.schemas import Schemas


def transform_device(
    *,
    device: Device,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for registered_device in device.RegisteredDevices:
        did = str(registered_device.deviceId)
        if did in metadata.device_ids_seen:
            continue
        transformed: dict[str, Any] = {
            "id": did,
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
        metadata.device_ids_seen.add(did)
    return entries


def transform_device_from_fit(
    *,
    fit: FITResult,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> dict[str, Any] | None:
    did = str(fit.device_id)
    if did in metadata.device_ids_seen:
        return None
    transformed: dict[str, Any] = {
        "id": did,
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
    metadata.device_ids_seen.add(did)
    return transformed
