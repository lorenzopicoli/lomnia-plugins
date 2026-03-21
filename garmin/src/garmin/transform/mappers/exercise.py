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


def kmh_to_ms(speed_kmh: float) -> float:
    return speed_kmh / 3.6


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
        exercise: dict[str, Any] = remove_none_values({
            "entityType": "exercise",
            "version": "1",
            "id": f"{PLUGIN_NAME}_{timestamp.timestamp()}",
            "source": PLUGIN_NAME,
            "deviceId": str(fit.device_id),
            "name": fit.activity_name,
            "startedAt": iso_utc(session.start_time),
            "endedAt": iso_utc(session.end_time),
            "exerciseType": exercise_type,
            "distance": session.total_distance * 1000 if session.total_distance else None,
            "avgPace": kmh_to_min_per_km(session.avg_speed) if session.avg_speed else None,
            "avgHeartRate": session.avg_heart_rate,
            # Average cadence from Garmin is in cycles (?) per minute. We want steps per minute
            "avgCadence": session.avg_cadence * 2 if session.avg_cadence else None,
            "feelScore": session.workout_feel,
            "perceivedEffort": session.workout_rpe,
            "laps": transform_exercise_laps(fit),
            "metrics": transform_exercise_metrics(fit),
        })

        if schemas.exercise is not None:
            try:
                jsonschema.validate(instance=exercise, schema=schemas.exercise)
            except jsonschema.ValidationError as e:
                print(f"Valid data validation error: {e.message}")
                raise

        metadata.record(
            "exercise",
            [datetime.fromisoformat(exercise["startedAt"]), datetime.fromisoformat(exercise["endedAt"])],
        )
        entries.append(exercise)

    return entries


def transform_exercise_laps(fit: FITResult) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for lap in fit.laps:
        if lap.start_time is None or lap.end_time is None:
            print("Skipping lap for lack of start/end time")
            continue
        entry: dict[str, Any] = remove_none_values({
            "id": f"{PLUGIN_NAME}_{lap.start_time.timestamp()}_{lap.end_time.timestamp()}",
            "startedAt": iso_utc(lap.start_time),
            "endedAt": iso_utc(lap.start_time),
            "distance": lap.total_distance * 1000 if lap.total_distance else None,
            "duration": lap.duration,
            "avgPace": kmh_to_min_per_km(lap.avg_speed) if lap.avg_speed else None,
            "maxPace": kmh_to_min_per_km(lap.max_speed) if lap.max_speed else None,
            "avgHeartRate": lap.avg_heart_rate,
            "maxHeartRate": lap.max_heart_rate,
            # Average cadence from Garmin is in cycles (?) per minute. We want steps per minute
            "avgCadence": lap.avg_cadence * 2 if lap.avg_cadence else None,
            "maxCadence": lap.max_cadence * 2 if lap.max_cadence else None,
            "avgStepLength": lap.avg_step_length,
            "avgVerticalOscillation": lap.avg_vertical_oscillation,
            "avgStanceTime": lap.avg_stance_time,
        })
        entries.append(entry)
    return entries


def transform_exercise_metrics(fit: FITResult) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for record in fit.records:
        if record.timestamp is None:
            print("Skipping record for lack of timestamp")
            continue

        metrics = {
            "id": f"{PLUGIN_NAME}_{record.timestamp}",
            "recordedAt": iso_utc(record.timestamp),
            "speed": kmh_to_ms(record.speed) if record.speed else None,
            "distance": record.distance * 1000 if record.distance else None,
            "cadence": record.cadence * 2 if record.cadence else None,
            "pace": kmh_to_min_per_km(record.speed) if record.speed else None,
            "stepLength": record.step_length,
            "verticalOscillation": record.vertical_oscillation,
            "stanceTime": record.stance_time,
        }

        has_real_data = any(
            metrics[key] is not None
            for key in [
                "speed",
                "distance",
                "cadence",
                "pace",
                "stepLength",
                "verticalOscillation",
                "stanceTime",
            ]
        )

        if not has_real_data:
            continue

        entry = remove_none_values(metrics)
        entries.append(entry)

    return entries
