from datetime import datetime, timezone

import jsonschema

from owntracks_recorder.transform.mappers.battery_status import get_batt_status
from owntracks_recorder.transform.mappers.connection_status import get_conn_status
from owntracks_recorder.transform.mappers.trigger import get_trigger
from owntracks_recorder.transform.mappers.utils.iso_utc import iso_utc
from owntracks_recorder.transform.mappers.utils.remove_none_values import remove_none_values
from owntracks_recorder.transform.run import TransformerParams


def transform_device_status(params: TransformerParams):
    location = params.data
    recorded_at: datetime = datetime.fromtimestamp(location.tst, tz=timezone.utc)
    transformed_device_status = remove_none_values({
        "id": location.id,
        "entityType": "deviceStatus",
        "source": "owntracks",
        "version": params.metadata.schemas["deviceStatus"],
        "deviceId": params.device,
        "battery": location.batt,
        "timezone": location.tzname,
        "recordedAt": iso_utc(recorded_at),
    })

    if location.SSID is not None:
        transformed_device_status["wifiSSID"] = location.SSID
    if trigger := get_trigger(location):
        transformed_device_status["trigger"] = trigger
    if batt_status := get_batt_status(location):
        transformed_device_status["batteryStatus"] = batt_status
    if conn_status := get_conn_status(location):
        transformed_device_status["connectionStatus"] = conn_status

    try:
        jsonschema.validate(instance=transformed_device_status, schema=params.schemas.device_status)
    except jsonschema.ValidationError as e:
        print(f"Device status validation error: {e.message}")
        raise
    params.metadata.record_device_status(recorded_at)
    return transformed_device_status
