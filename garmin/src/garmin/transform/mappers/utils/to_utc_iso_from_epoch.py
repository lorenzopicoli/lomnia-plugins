from datetime import datetime, timezone


def to_utc_iso_from_epoch(epoch: int | float) -> str:
    # Detect milliseconds
    if epoch > 1e12:
        epoch = epoch / 1000

    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
