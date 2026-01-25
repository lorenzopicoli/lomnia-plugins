from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LegacyLocation(BaseModel):
    model_config = ConfigDict(
        extra="ignore",  # ignore unexpected fields
        validate_assignment=True,  # re-validate on mutation if you ever change fields
    )

    id: Optional[int]

    lat: float
    lng: float

    accuracy: Optional[float] = None
    verticalAccuracy: Optional[float] = None
    velocity: Optional[float] = None
    altitude: Optional[float] = None

    battery: Optional[int] = None
    trigger: Optional[str] = None
    batteryStatus: Optional[int] = None
    connectionStatus: Optional[str] = None
    wifiSSID: Optional[str] = None

    timezone: Optional[str] = None
    recorded_at: datetime

    source: str = Field(default="legacy_locations_sqlite")
    topic: Optional[str] = None
