import jsonschema

from legacy_locations.transform.mappers.transformer_params import TransformerParams
from legacy_locations.transform.mappers.utils.iso_utc import iso_utc


def transform_location(params: TransformerParams):
    data = params.data
    transformed = {
        "id": "legacy_" + str(data.id),
        "entityType": "location",
        "version": "1",
        "deviceId": params.device,
        "source": data.source,
        "accuracy": data.accuracy,
        "verticalAccuracy": data.verticalAccuracy,
        "velocity": data.velocity,
        "altitude": data.altitude,
        "location": {"lat": data.lat, "lng": data.lng},
        "timezone": data.timezone,
        "recordedAt": iso_utc(data.recorded_at),
    }

    if data.topic:
        transformed["topic"] = data.topic

    if params.schemas.location is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.location)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record_location(data.recorded_at)
    return transformed
