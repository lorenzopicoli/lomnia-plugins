from datetime import datetime, timezone


def normalize_row(row: dict) -> dict:
    raw = row["raw"]
    if "lat" in raw and "lon" in raw:
        ts = datetime.fromtimestamp(raw["tst"], tz=timezone.utc)
        return {
            "id": raw.get("_id"),
            "lat": raw["lat"],
            "lng": raw["lon"],
            "accuracy": raw.get("acc"),
            "verticalAccuracy": raw.get("vac"),
            "velocity": raw.get("vel"),
            "altitude": raw.get("alt"),
            "battery": raw.get("batt"),
            "batteryStatus": raw.get("bs"),
            "trigger": raw.get("t"),
            "connectionStatus": raw.get("conn"),
            "wifiSSID": raw.get("SSID"),
            "timezone": raw.get("tzname"),
            "recorded_at": ts,
            "source": "legacy_locations_owntracks",
            "topic": raw.get("topic"),
        }

    ts = datetime.fromisoformat(raw["timestamp"].replace("Z", "+00:00"))
    return {
        "id": row.get("row_id"),
        "lat": raw["latitude"],
        "lng": raw["longitude"],
        "accuracy": raw.get("accuracy"),
        "verticalAccuracy": raw.get("verticalAccuracy"),
        "velocity": raw.get("velocity"),
        "altitude": raw.get("altitude"),
        "battery": raw.get("battery"),
        "trigger": raw.get("triggerType"),
        "batteryStatus": raw.get("batteryStatus"),
        "connectionStatus": raw.get("connectionStatus"),
        "wifiSSID": raw.get("wifiSSID"),
        "timezone": row.get("timezone"),
        "recorded_at": ts,
        "source": "legacy_locations_sqlite",
        "topic": raw.get("originalPublishTopic"),
    }
