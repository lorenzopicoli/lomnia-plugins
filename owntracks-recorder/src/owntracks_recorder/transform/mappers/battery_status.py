from owntracks_recorder.transform.api import OwntracksLocation


def get_batt_status(location: OwntracksLocation) -> str | None:
    mapping = {
        0: "unknown",
        1: "unplugged",
        2: "charging",
        3: "full",
    }
    if location.batt is None:
        return None
    return mapping.get(location.batt, None)
