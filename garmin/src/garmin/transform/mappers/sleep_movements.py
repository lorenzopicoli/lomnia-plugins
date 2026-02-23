from collections import defaultdict
from datetime import timedelta

from garmin.transform.models.sleep import Sleep


def sleep_movement_to_stage(sleep: Sleep):
    events = sleep.sleepLevels
    totals = defaultdict(timedelta)

    for event in events:
        start = event.startGMT
        end = event.endGMT
        stage = event.activityLevel

        duration = end - start
        totals[stage] += duration

        print(f"{stage}: {start} → {end} ({duration.total_seconds() / 60:.1f} min)")

    # ---- Print totals ----
    print("\n--- Totals ---")
    for stage in sorted(totals.keys()):
        minutes = totals[stage].total_seconds() / 60
        print(f"{stage}: {minutes:.1f} min")
