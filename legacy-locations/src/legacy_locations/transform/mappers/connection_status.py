def get_conn_status(status: str) -> str | None:
    mapping = {
        "wifi": "wifi",
        "offline": "offline",
        "data": "cellular",
        "unknown": "unknown",
        "w": "wifi",
        "o": "offline",
        "m": "cellular",
    }
    return mapping.get(status)
