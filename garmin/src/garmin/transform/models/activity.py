from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ActivityDeviceStatus:
    timestamp: datetime
    battery_level: Optional[int]
    temperature: Optional[float]


@dataclass
class ActivityUserMetrics:
    timestamp: datetime
    vo2_max: Optional[float]
    max_hr: Optional[int]
    lthr: Optional[int]


@dataclass
class ActivityTrainingSettings:
    # IGNORE
    self_evaluation: Optional[str]


@dataclass
class ActivityRecord:
    timestamp: Optional[datetime]
    heart_rate: Optional[int]
    distance: Optional[float]
    body_battery: Optional[int]
    cadence: Optional[int]
    speed: Optional[float]
    step_length: Optional[float]
    stance_time: Optional[float]
    lat: Optional[float]
    lng: Optional[float]
    altitude: Optional[float]
    vertical_oscillation: Optional[float]


@dataclass
class ActivitySession:
    timestamp: Optional[datetime]
    sport: Optional[str]
    sub_sport: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_distance: Optional[float]
    avg_heart_rate: Optional[float]
    avg_cadence: Optional[float]
    avg_speed: Optional[float]
    workout_rpe: Optional[int]
    workout_feel: Optional[int]


@dataclass
class ActivityLap:
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    total_distance: Optional[float]
    duration: Optional[float]
    total_strides: Optional[int]

    avg_speed: Optional[float]
    max_speed: Optional[float]

    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]

    avg_cadence: Optional[int]
    max_cadence: Optional[int]

    avg_step_length: Optional[float]
    avg_vertical_oscillation: Optional[float]
    avg_stance_time: Optional[float]
