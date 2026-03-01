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
    self_evaluation: Optional[int]


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
    vertical_oscillation: Optional[float]


@dataclass
class ActivitySession:
    timestamp: Optional[datetime]
    sport: Optional[str]
    sub_sport: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_distance: Optional[float]
