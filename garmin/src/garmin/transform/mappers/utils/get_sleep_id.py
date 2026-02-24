from garmin.config import PLUGIN_NAME
from garmin.transform.models.sleep import Sleep


def get_sleep_id(sleep: Sleep):
    return f"{PLUGIN_NAME}_{sleep.dailySleepDTO.id}"
