import gzip
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jsonlines import jsonlines


@dataclass
class TransformerParams:
    device: str
    out_dir: Path
    in_dir: Path


def run_transform(params: TransformerParams):
    file_name = os.path.join(params.out_dir, f"{get_file_name(datetime.now(timezone.utc))}")
    canon_file = f"{file_name}.jsonl.gz"
    metadata_file = f"{file_name}.meta.json"

    is_device_saved = False

    with gzip.open(canon_file, "wt", encoding="utf-8") as gz:
        writer = jsonlines.Writer(gz)
        for response in getApiResponses(args.in_dir):
            for location in response.data:
                if not is_device_saved:
                    # Currently only support one user/device
                    writer.write(transform_device())

                writer.write(transform_location(location))
                writer.write(transform_device_status(location))
    with Path(metadata_file).open("w", encoding="utf-8") as f:
        json.dump(run_metadata.to_dict(), f, indent=2)
