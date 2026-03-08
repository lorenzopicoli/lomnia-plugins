from datetime import datetime
from typing import Any

import jsonschema

from garmin.config import PLUGIN_NAME
from garmin.transform.mappers.utils.iso_utc import iso_utc
from garmin.transform.mappers.utils.remove_none_values import remove_none_values
from garmin.transform.meta import TransformRunMetadata
from garmin.transform.parsers.activity import FITResult
from garmin.transform.schemas import Schemas


def kmh_to_min_per_km(speed_kmh: float) -> float:
    return 60 / speed_kmh


def transform_exercise(
    *,
    fit: FITResult,
    metadata: TransformRunMetadata,
    schemas: Schemas,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for session in fit.sessions:
        timestamp = session.timestamp
        if timestamp is None or session.start_time is None or session.end_time is None:
            print("Skipping session for not having a timezone or start/end date", fit.activity_name)
            continue

        exercise_type = (
            session.sub_sport if session.sport == "training" or session.sport == "generic" else session.sport
        )
        transformed: dict[str, Any] = remove_none_values({
            "entityType": "exercise",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "deviceId": str(fit.device_id),
            "name": fit.activity_name,
            "startedAt": iso_utc(session.start_time),
            "endedAt": iso_utc(session.end_time),
            "exerciseType": exercise_type,
            "distance": session.total_distance,
            "avgPace": kmh_to_min_per_km(session.avg_speed) if session.avg_speed else None,
            "avgHeartRate": session.avg_heart_rate,
            # Average cadence from Garmin is in cycles (?) per minute. We want steps per minute
            "avgCadence": session.avg_cadence * 2 if session.avg_cadence else None,
            "selfEvaluation": fit.training_settings.pop().self_evaluation,
        })

        if schemas.exercise is not None:
            try:
                jsonschema.validate(instance=transformed, schema=schemas.exercise)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "exercise",
            [datetime.fromisoformat(transformed["startedAt"]), datetime.fromisoformat(transformed["endedAt"])],
        )
        entries.append(transformed)

    return entries
