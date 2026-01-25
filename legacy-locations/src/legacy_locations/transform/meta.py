from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from legacy_locations.config import PACKAGE_NAME
from legacy_locations.version import get_version


@dataclass
class TransformRunMetadata:
    transformer: str = PACKAGE_NAME
    transformer_version: str = get_version()

    files_processed: list[str] = field(default_factory=list)

    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None

    start_date: Optional[datetime] = None

    counts: dict[str, int] = field(
        default_factory=lambda: {
            "device": 0,
            "location": 0,
            "device_status": 0,
        }
    )

    def add_files_processed(self, path: Path) -> None:
        self.files_processed.append(path.name)

    def start(self) -> None:
        self.start_date = datetime.now(timezone.utc)

    def record_device(self) -> None:
        self._inc("device")

    def record_location(self, recorded_at: datetime) -> None:
        self._inc("location")
        self._update_time_bounds(recorded_at)

    def record_device_status(self, recorded_at: datetime) -> None:
        self._inc("device_status")
        self._update_time_bounds(recorded_at)

    def _inc(self, key: str) -> None:
        self.counts[key] += 1

    def _update_time_bounds(self, ts: datetime) -> None:
        if self.min_date is None or ts < self.min_date:
            self.min_date = ts
        if self.max_date is None or ts > self.max_date:
            self.max_date = ts

    def to_dict(self) -> dict:
        return {
            "transformer": self.transformer,
            "transformer_version": self.transformer_version,
            "transform_start": self.start_date.isoformat() if self.start_date else None,
            "transform_end": datetime.now(timezone.utc).isoformat(),
            "inputs": self.files_processed,
            "window_start": (self.min_date.isoformat() if self.min_date else None),
            "window_end": (self.max_date.isoformat() if self.max_date else None),
            "counts": self.counts,
        }
