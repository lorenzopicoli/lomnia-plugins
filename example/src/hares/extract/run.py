import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from hares.extract.meta import write_meta_file


@dataclass
class ExtractionParams:
    start_date: datetime
    out_dir: Path
    in_dir: Path


def run_extract(params: ExtractionParams):
    extract_start = datetime.now(timezone.utc)

    # Example: read all files in a folder and copy them as they are to the out_dir
    for path in Path(params.in_dir).rglob("*"):
        if not path.is_file():
            continue

        suffix = "".join(path.suffixes)
        base = path.name.removesuffix(suffix)

        file_name = f"{base}_{str(uuid.uuid4()).split('-')[0]}"
        raw_file_name = f"{file_name}{suffix}"
        dest_path = params.out_dir / raw_file_name

        shutil.copy2(path, dest_path)

        write_meta_file(
            out_dir=params.out_dir,
            source_path=path,
            file_name=file_name,
            extract_start=extract_start,
        )

        print(f"Copied file {path}")
