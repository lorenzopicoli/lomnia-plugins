def get_trigger(trigger: str) -> str | None:
    mapping = {
        "p": "ping",
        "c": "circular",
        "r": "report_location",
        "u": "manual",
    }
    return mapping.get(trigger, trigger)
