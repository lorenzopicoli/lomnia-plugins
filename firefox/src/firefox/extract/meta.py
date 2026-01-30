import json
from datetime import datetime, timezone
from pathlib import Path

from firefox.config import PACKAGE_NAME
from firefox.version import get_version


def write_meta_file(
    *,
    out_dir: Path,
    extract_start: datetime,
    source_path: Path,
    file_name: str,
) -> Path:
    meta = {
        "data_window_start": None,
        "data_window_end": None,
        "extractor_version": get_version(),
        "extractor": PACKAGE_NAME,
        "extract_start": extract_start.isoformat(),
        "extract_end": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_path),
    }

    meta_name = f"{file_name}.meta.json"
    meta_path = out_dir / meta_name
    _ = meta_path.write_text(json.dumps(meta, indent=2))

    return meta_path
