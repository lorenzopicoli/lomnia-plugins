
import uuid

import jsonschema

from legacy_locations.common.helpers import iso_utc
from legacy_locations.transform.transformer_run_metadata import TransformRunMetadata


def transform_location(normalized: dict, device: str, schema: dict, run_metadata: TransformRunMetadata) -> dict:
    transformed = {
        "id": str(uuid.uuid4()),
        "entityType": "location",
        "version": run_metadata.schemas["location"],
        "deviceId": device,
        "source": normalized["source"],
        "accuracy": normalized["accuracy"],
        "verticalAccuracy": normalized["verticalAccuracy"],
        "velocity": normalized["velocity"],
        "altitude": normalized["altitude"],
        "location": {
            "lat": normalized["lat"],
            "lng": normalized["lng"],
        },
        "timezone": normalized["timezone"],
        "recordedAt": iso_utc(normalized["recorded_at"]),
    }

    if normalized.get("topic"):
        transformed["topic"] = normalized["topic"]

    run_metadata.record_location(normalized["recorded_at"])
    return transformed


def transform_device_status(normalized: dict, device: str, schema: dict, run_metadata: TransformRunMetadata) -> dict:
    transformed = {
        "id": str(uuid.uuid4()),
        "entityType": "deviceStatus",
        "version": run_metadata.schemas["deviceStatus"],
        "deviceId": device,
        "battery": normalized["battery"],
        "recordedAt": iso_utc(normalized["recorded_at"]),
    }

    if normalized.get("wifiSSID"):
        transformed["wifiSSID"] = normalized["wifiSSID"]

    if normalized.get("batteryStatus") is not None:
        transformed["batteryStatus"] = normalized["batteryStatus"]

    if normalized.get("connectionStatus"):
        transformed["connectionStatus"] = normalized["connectionStatus"]

    run_metadata.record_device_status(normalized["recorded_at"])
    return transformed


def transform_device(device: str, schema: dict, run_metadata: TransformRunMetadata):
    transformed_device = {
        "id": device,
        "entityType": "device",
        "source": "legacy_locations",
        "version": run_metadata.schemas["device"],
    }
    try:
        jsonschema.validate(
            instance=transformed_device, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"Valid data validation error: {e.message}")
        raise
    run_metadata.record_device()
    return transformed_device
