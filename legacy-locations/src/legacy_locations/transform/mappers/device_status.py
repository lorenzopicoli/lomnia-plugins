import jsonschema

from legacy_locations.transform.mappers.battery_status import get_batt_status
from legacy_locations.transform.mappers.connection_status import get_conn_status
from legacy_locations.transform.mappers.transformer_params import TransformerParams
from legacy_locations.transform.mappers.utils.iso_utc import iso_utc


def transform_device_status(params: TransformerParams):
    data = params.data
    transformed = {
        "id": "legacy_" + str(data.id),
        "entityType": "deviceStatus",
        "version": "1",
        "deviceId": params.device,
        "battery": data.battery,
        "source": data.source,
        "timezone": data.timezone,
        "recordedAt": iso_utc(data.recorded_at),
    }

    if data.wifiSSID:
        transformed["wifiSSID"] = data.wifiSSID

    if batt_status := get_batt_status(data.batteryStatus):
        transformed["batteryStatus"] = batt_status

    if data.connectionStatus:
        transformed["connectionStatus"] = get_conn_status(data.connectionStatus)

    if params.schemas.device_status is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.device_status)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record_device_status(data.recorded_at)

    return transformed
