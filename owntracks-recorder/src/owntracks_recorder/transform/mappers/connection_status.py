from enum import Enum

from owntracks_recorder.transform.api import OwntracksLocation


class ConnectivityStatus(str, Enum):
    w = "w"
    o = "o"
    m = "m"


def get_conn_status(location: OwntracksLocation) -> str | None:
    mapping = {
        "w": "wifi",
        "o": "offline",
        "m": "cellular",
    }
    if location.conn is None:
        return None
    return mapping.get(location.conn, None)
