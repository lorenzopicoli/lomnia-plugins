import uuid
from datetime import datetime, timezone


def iso_utc(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp_for_file_name(time: datetime) -> str:
    return str(int(time.timestamp()))


def get_short_uid() -> str:
    return str(uuid.uuid4()).split("-")[0]
