from datetime import datetime, timezone
from typing import Optional


def microseconds_to_datetime(date: Optional[int]) -> Optional[datetime]:
    if date is None:
        return None

    return datetime.fromtimestamp(date / 1_000_000, tz=timezone.utc)
