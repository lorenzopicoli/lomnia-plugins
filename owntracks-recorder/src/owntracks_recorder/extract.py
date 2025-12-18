import argparse
import gzip
import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import NamedTuple

import httpx
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass

load_dotenv()


@dataclass
class ExtractorEnvVars:
    user: str = os.environ["OWNTRACKS_USER"]
    device: str = os.environ["OWNTRACKS_DEVICE"]
    server_url: str = os.environ["OWNTRACKS_URL"]


class ExtractorArgs(NamedTuple):
    start_date: datetime
    out_dir: Path


class MissingEnvVar(ValueError):
    def __init__(self, value):
        self.value = value
        message = f"Missing env var: {value}"
        super().__init__(message)


class FailedToExtract(ValueError):
    def __init__(self, value):
        super().__init__(value)


def get_version() -> str:
    try:
        return version("owntracks_recorder")
    except PackageNotFoundError:
        return "unknown"


def timestamp_for_file_name(time: datetime) -> str:
    return str(int(time.timestamp()))


def get_short_uid() -> str:
    return str(uuid.uuid4()).split("-")[0]


def get_file_name(start: datetime, end: datetime) -> str:
    service = "owntracks"
    return f"{service}_{timestamp_for_file_name(start)}_{timestamp_for_file_name(end)}_{get_short_uid()}"


def write_meta_file(
    *,
    out_dir: Path,
    window_start: datetime,
    window_end: datetime,
    extractor_version: str,
    service_version: str,
    extract_start: datetime,
    file_name: str
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


def parse_extract_args() -> ExtractorArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_date",
        required=True,
        type=lambda value: datetime.fromtimestamp(
            float(value), tz=timezone.utc),
        help="Start date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "--out_dir",
        required=True,
        type=Path,
        help="Output directory path"
    )

    args = parser.parse_args()
    print("Start date:", args.start_date)
    print("Output dir:", args.out_dir)
    return ExtractorArgs(start_date=args.start_date, out_dir=args.out_dir)

# Maybe one day when I support multiple users
# def get_user_devices(client: httpx.Client):
#     users = client.get("/api/0/list")
#     user_devices = []
#     for user in users.json()["results"]:
#         devices = client.get("/api/0/list", params={"user": user})
#         print(devices.json())
#         for device in devices.json()["results"]:
#             user_devices.append((user, device))
#     return user_devices


def write_results(
    client: httpx.Client,
    user: str,
    device: str,
    start_date: datetime,
    out_dir: Path,
) -> datetime | None:
    params = {
        "user": user,
        "device": device,
    }

    curr_date = start_date
    extract_start = datetime.now(timezone.utc)
    last_request_date: datetime | None = None

    while curr_date < datetime.now(tz=timezone.utc) - timedelta(seconds=10):
        next_date = min(
            curr_date + timedelta(days=1),
            datetime.now(tz=timezone.utc),
        )

        headers = {
            "X-Limit-From": curr_date.isoformat(),
            "X-Limit-To": next_date.isoformat(),
        }

        print(
            f"Fetching data from {headers['X-Limit-From']} to {headers['X-Limit-To']}"
        )

        file_name = get_file_name(curr_date, next_date)
        raw_file_name = f"{file_name}.json.gz"
        raw_path = out_dir / raw_file_name

        version_response = client.get("/api/0/version")
        version = version_response.json()["version"]

        with client.stream(
            "GET",
            "/api/0/locations",
            params=params,
            headers=headers,
        ) as http_stream, gzip.open(raw_path, "wb") as out:
            for chunk in http_stream.iter_bytes():
                out.write(chunk)

        write_meta_file(
            out_dir=out_dir,
            window_start=curr_date,
            window_end=next_date,
            extractor_version=get_version(),
            service_version=version,
            extract_start=extract_start,
            file_name=file_name
        )

        last_request_date = next_date
        curr_date = next_date

    return last_request_date


def extract() -> datetime:
    args = parse_extract_args()
    settings = ExtractorEnvVars()

    last_request: date | None = None
    with httpx.Client(base_url=settings.server_url, timeout=30.0) as client:
        last_request = write_results(client, user=settings.user, device=settings.device,
                                     start_date=args.start_date, out_dir=args.out_dir)

    if last_request is None:
        raise FailedToExtract("NO_REQUEST_VALUE")
    return last_request


def main():
    extract()


if __name__ == "__main__":
    main()
