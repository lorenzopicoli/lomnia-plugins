import gzip
import json
from datetime import datetime
from pathlib import Path

from legacy_locations.transform.meta import TransformRunMetadata
from legacy_locations.transform.models import LegacyLocation


def get_rows(in_dir: Path, metadata: TransformRunMetadata):
    for path in in_dir.iterdir():
        if path.is_file() and ".jsonl" in path.suffixes and ".gz" in path.suffixes and ".meta" not in path.suffixes:
            metadata.add_files_processed(path)
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    raw = row["raw"]
                    ts = datetime.fromisoformat(raw["timestamp"].replace("Z", "+00:00"))
                    yield LegacyLocation(
                        id=row.get("row_id"),
                        lat=raw["latitude"],
                        lng=raw["longitude"],
                        accuracy=raw.get("accuracy"),
                        verticalAccuracy=raw.get("verticalAccuracy"),
                        velocity=raw.get("velocity"),
                        altitude=raw.get("altitude"),
                        battery=raw.get("battery"),
                        trigger=raw.get("triggerType"),
                        batteryStatus=raw.get("batteryStatus"),
                        connectionStatus=raw.get("connectionStatus"),
                        wifiSSID=raw.get("wifiSSID"),
                        timezone=row.get("timezone"),
                        recorded_at=ts,
                        topic=raw.get("originalPublishTopic"),
                    )
