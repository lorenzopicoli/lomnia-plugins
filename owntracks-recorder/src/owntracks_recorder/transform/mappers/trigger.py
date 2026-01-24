from owntracks_recorder.transform.api import OwntracksLocation, TriggerType


def get_trigger(location: OwntracksLocation) -> str | None:
    mapping = {
        TriggerType.p: "ping",
        TriggerType.c: "circular",
        TriggerType.r: "report_location",
        TriggerType.u: "manual",
    }
    if location.t is None:
        return None
    return mapping.get(location.t)
