import json
from datetime import datetime, timezone
from pathlib import Path


def write_meta_file(
    *,
    out_dir: Path,
    window_start: datetime,
    window_end: datetime,
    extractor_version: str,
    service_version: str,
    extract_start: datetime,
    file_name: str,
) -> Path:
    meta = {
        "data_window_start": window_start.isoformat(),
        "data_window_end": window_end.isoformat(),
        "extractor_version": extractor_version,
        "extractor": "owntracks_recorder",
        "service_version": service_version,
        "extract_start": extract_start.isoformat(),
        "extract_end": datetime.now(timezone.utc).isoformat(),
    }

    meta_name = f"{file_name}.meta.json"

    meta_path = out_dir / meta_name
    meta_path.write_text(json.dumps(meta, indent=2))

    return meta_path
