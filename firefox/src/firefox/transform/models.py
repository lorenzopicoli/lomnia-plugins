from typing import Optional

from pydantic import BaseModel, Field


class MozPlace(BaseModel):
    id: int

    url: Optional[str] = None
    title: Optional[str] = None
    rev_host: Optional[str] = None

    visit_count: int = Field(default=0, ge=0)
    hidden: int = Field(default=0, ge=0)
    typed: int = Field(default=0, ge=0)

    frecency: int = Field(default=-1)
    last_visit_date: Optional[int] = None  # microseconds since epoch

    guid: Optional[str] = None

    foreign_count: int = Field(default=0, ge=0)
    url_hash: int = Field(default=0)

    description: Optional[str] = None
    preview_image_url: Optional[str] = None
    site_name: Optional[str] = None

    origin_id: Optional[int] = None

    recalc_frecency: int = Field(default=0)
    alt_frecency: Optional[int] = None
    recalc_alt_frecency: int = Field(default=0)

    model_config = {
        "extra": "forbid",
    }


class MozHistoryVisit(BaseModel):
    id: int
    # Row number, just to make pydantic happy without having to list out all of the table's columns
    rn: int

    from_visit: Optional[int] = None
    place_id: Optional[int] = None

    visit_date: int  # microseconds since epoch
    visit_type: Optional[int] = None
    session: Optional[int] = None

    source: int = Field(default=0, ge=0)
    triggeringPlaceId: Optional[int] = None

    # Joined
    place_guid: Optional[str] = None
    # Joined
    downloaded_file: Optional[str] = None

    from_visit_place_guid: Optional[str] = None

    from_visit_visit_date: Optional[int] = None  # microseconds since epoch
    from_visit_visit_type: Optional[int] = None

    model_config = {
        "extra": "forbid",
    }
