def get_batt_status(status: int | None) -> str | None:
    mapping = {
        0: "unknown",
        1: "unplugged",
        2: "charging",
        3: "full",
    }
    if status is None:
        return None

    map_result = mapping.get(status)
    if map_result is None:
        print(f"Failed to map battery status {status}")
    return map_result
