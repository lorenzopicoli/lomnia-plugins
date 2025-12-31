

import jsonschema

from legacy_locations.common.helpers import iso_utc
from legacy_locations.transform.transformer_run_metadata import TransformRunMetadata


def get_conn_status(status: str) -> str | None:
    mapping = {
        "wifi": "wifi",
        "offline": "offline",
        "data": "cellular",
        "unknown": "unknown",
        "w": "wifi",
        "o": "offline",
        "m": "cellular",
    }
    if status is None:
        return None
    return mapping.get(status)


def get_trigger(trigger: str) -> str | None:
    mapping = {
        "p": "ping",
        "c": "circular",
        "r": "report_location",
        "u": "manual",
    }
    if trigger is None:
        return None
    return mapping.get(trigger, trigger)


def get_batt_status(status: int) -> str | None:
    mapping = {
        0: "unknown",
        1: "unplugged",
        2: "charging",
        3: "full",
    }
    if status is None:
        return None

    map_result = mapping.get(status)
    if map_result is None:
        print(f"Failed to map battery status {status}")
    return map_result


def transform_location(normalized: dict, device: str, schema: dict | None, run_metadata: TransformRunMetadata) -> dict:
    transformed = {
        "id": "legacy_" + str(normalized["id"]),
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

    if schema is not None:
        try:
            jsonschema.validate(
                instance=transformed, schema=schema)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    run_metadata.record_location(normalized["recorded_at"])
    return transformed


def transform_device_status(normalized: dict, device: str, schema: dict | None, run_metadata: TransformRunMetadata) -> dict:
    transformed = {
        "id": "legacy_" + str(normalized["id"]),
        "entityType": "deviceStatus",
        "version": run_metadata.schemas["deviceStatus"],
        "deviceId": device,
        "battery": normalized["battery"],
        "source": normalized["source"],
        "timezone": normalized["timezone"],
        "recordedAt": iso_utc(normalized["recorded_at"]),
    }

    if normalized.get("wifiSSID"):
        transformed["wifiSSID"] = normalized["wifiSSID"]

    if (batt_status := get_batt_status(normalized["batteryStatus"])):
        transformed["batteryStatus"] = batt_status

    if normalized.get("connectionStatus"):
        transformed["connectionStatus"] = get_conn_status(
            normalized["connectionStatus"])

    if normalized.get("connectionStatus"):
        transformed["connectionStatus"] = get_conn_status(
            normalized["connectionStatus"])

    if schema is not None:
        try:
            jsonschema.validate(
                instance=transformed, schema=schema)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    run_metadata.record_device_status(normalized["recorded_at"])

    return transformed


def transform_device(device: str, schema: dict | None, run_metadata: TransformRunMetadata):
    transformed_device = {
        "id": device,
        "entityType": "device",
        "source": "legacy_locations",
        "version": run_metadata.schemas["device"],
    }
    if schema is not None:
        try:
            jsonschema.validate(
                instance=transformed_device, schema=schema)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    run_metadata.record_device()
    return transformed_device
