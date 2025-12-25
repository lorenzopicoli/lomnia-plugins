
from datetime import datetime

from legacy_locations.common.helpers import timestamp_for_file_name
from legacy_locations.extract import get_short_uid


def get_file_name(date: datetime) -> str:
    service = "legacy_locations"
    return f"{service}_canon_{timestamp_for_file_name(date)}_{get_short_uid()}"
