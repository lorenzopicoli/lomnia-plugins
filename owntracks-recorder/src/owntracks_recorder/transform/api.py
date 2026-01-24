import gzip
import json
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from owntracks_recorder.transform.meta import TransformRunMetadata


class TriggerType(str, Enum):
    """
    Trigger type
    - p ping issued randomly by background task (iOS,Android)
    - c circular region enter/leave event (iOS,Android)
    - C circular region enter/leave event for +follow regions (iOS)
    - b beacon region enter/leave event (iOS)
    - r response to a reportLocation cmd message (iOS,Android)
    - u manual publish requested by the user (iOS,Android)
    - t timer based publish in move move (iOS)
    - v updated by Settings/Privacy/Locations Services/System Services/Frequent Locations monitoring (iOS)
    """

    p = "p"
    c = "c"
    C = "C"
    b = "b"
    r = "r"
    u = "u"
    t = "t"
    v = "v"


class ConnectivityStatus(str, Enum):
    w = "w"
    o = "o"
    m = "m"


class OwntracksLocation(BaseModel):
    type: str = Field("location", pattern="^location$", alias="_type")

    source: Optional[str] = Field(
        None, pattern="^(network|fused|gps)$", description="The source of the datapoint hardware-wise"
    )

    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    tst: int = Field(..., gt=0, description="Timestamp in UNIX format (seconds since epoch)")

    acc: Optional[int] = Field(None, description="Accuracy in meters")
    alt: Optional[int] = Field(None, description="Altitude in meters")
    batt: Optional[int] = Field(None, ge=0, le=100, description="Battery percentage")
    bs: Optional[int] = Field(None, ge=0, le=3, description="Battery Status 0=unknown, 1=unplugged, 2=charging, 3=full")
    cog: Optional[int] = Field(None, description="Course over ground in degrees")
    rad: Optional[int] = Field(None, gt=0, description="Radius in meters")

    t: Optional[TriggerType] = Field(None, description="")
    tid: Optional[str] = Field(None, description="Tracker id")
    vac: Optional[int] = Field(None, description="Vertical accuracy in meters")
    vel: Optional[int] = Field(None, ge=0, description="Velocity in km/h")

    # Extended data fields (only if extendedData=true)
    p: Optional[float] = Field(None, description="Barometric pressure in kPa")
    conn: Optional[ConnectivityStatus] = Field(
        None,
        description="w=phone is connected to a WiFi connection (iOS,Android), o=phone is offline (iOS,Android), m=mobile data (iOS,Android)",
    )

    # iOS Fields
    poi: Optional[str] = Field(None, description="Point of interest name")
    image: Optional[str] = Field(None, description="Base64 encoded image")
    imagename: Optional[str] = Field(None, description="Image name")
    tag: Optional[str] = Field(None, description="Tag name")
    SSID: Optional[str] = Field(None, description="Wifi SSID")
    BSSID: Optional[str] = Field(None, description="WiFi access point identifier")
    m: Optional[int] = Field(None, ge=1, le=2)

    inregions: Optional[list[str]] = Field(None, description="List of region names")
    inrids: Optional[list[str]] = Field(None, description="List of region IDs")

    # HTTP mode fields
    topic: Optional[str] = Field(None, description="Original publish topic")
    # Android Fields
    id: Optional[str] = Field(None, description="Random identifier", alias="_id")

    created_at: Optional[int] = Field(None, gt=0, description="Message creation timestamp (seconds since epoch)")
    isorcv: Optional[str] = Field(None, description="Received timestamp in ISO format (UTC)")
    isotst: Optional[str] = Field(None, description="Publish timestamp in ISO format (UTC)")
    disptst: Optional[str] = Field(None, description="Publish timestamp in display format")
    tzname: Optional[str] = Field(None, description='Timezone name (e.g. "Europe/Berlin")')
    ghash: Optional[str] = Field(None, description="Hash that represents the location")
    isolocal: Optional[str] = Field(None, description='Date/time in the user timezone (eg. "2025-01-14T18:43:09-0500")')

    http: Optional[bool] = Field(None, description="", alias="_http")

    # To get warned of new fields or breaking changes in the API
    model_config = {"extra": "forbid"}


class OwntracksLocationApiResponse(BaseModel):
    count: Optional[int] = Field(None, description="")
    data: list[OwntracksLocation]
    status: int
    version: str

    model_config = {"extra": "forbid"}


# TODO: Probably want to yield each api response and not load everything in memory
def getApiResponses(in_dir: Path, metadata: TransformRunMetadata):
    responses: list[OwntracksLocationApiResponse] = []
    for path in in_dir.iterdir():
        if path.is_file() and path.suffix == ".gz":
            print(f"Loading file: {path.name}")
            metadata.add_file_processed(path)
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
                responses.append(OwntracksLocationApiResponse(**data))
    return responses
