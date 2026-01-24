from datetime import datetime, timezone

import jsonschema

from owntracks_recorder.transform.mappers.trigger import get_trigger
from owntracks_recorder.transform.mappers.utils.iso_utc import iso_utc
from owntracks_recorder.transform.mappers.utils.remove_none_values import remove_none_values
from owntracks_recorder.transform.run import TransformerParams


def transform_location(params: TransformerParams):
    location = params.data

    recorded_at: datetime = datetime.fromtimestamp(location.tst, tz=timezone.utc)
    transformed_loc = remove_none_values({
        "version": "1",
        "id": location.id,
        "entityType": "location",
        "deviceId": params.device,
        "source": "owntracks",
        "gpsSource": location.source,
        "accuracy": location.acc,
        "verticalAccuracy": location.vac,
        "velocity": location.vel,
        "altitude": location.alt,
        "location": {"lat": location.lat, "lng": location.lon},
        "topic": location.topic,
        "timezone": location.tzname,
        "recordedAt": iso_utc(recorded_at),
    })

    if trigger := get_trigger(location):
        transformed_loc["trigger"] = trigger

    try:
        jsonschema.validate(instance=transformed_loc, schema=params.schemas.location)
    except jsonschema.ValidationError as e:
        print(f"Location validation error: {e.message}")
        raise
    params.metadata.record_location(recorded_at)
    return transformed_loc
