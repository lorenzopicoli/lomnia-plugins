import gzip
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx

from owntracks_recorder.config import PLUGIN_NAME
from owntracks_recorder.extract.meta import write_meta_file


class FailedToExtract(ValueError):
    pass


@dataclass
class ExtractionParams:
    user: str
    device: str
    server_url: str

    start_date: datetime
    out_dir: Path


def timestamp(time: datetime) -> str:
    return str(int(time.timestamp()))


def run_extract(params: ExtractionParams):
    last_request: date | None = None
    with httpx.Client(base_url=params.server_url, timeout=30.0) as client:
        last_request = write_results(client, params)

    if last_request is None:
        raise FailedToExtract("NO_REQUEST_VALUE")
    return last_request


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


def write_results(client: httpx.Client, params: ExtractionParams) -> datetime | None:
    api_params = {
        "user": params.user,
        "device": params.device,
    }

    curr_date = params.start_date
    extract_start = datetime.now(timezone.utc)
    last_request_date: datetime | None = None
    # Only do X days at a time
    days_left = 50

    while curr_date < datetime.now(tz=timezone.utc) - timedelta(seconds=10):
        days_left -= 1
        next_date = min(
            curr_date + timedelta(days=1),
            datetime.now(tz=timezone.utc),
        )

        headers = {
            "X-Limit-From": curr_date.isoformat(),
            "X-Limit-To": next_date.isoformat(),
        }

        print(f"Fetching data from {headers['X-Limit-From']} to {headers['X-Limit-To']}")

        file_name = f"{PLUGIN_NAME}_{timestamp(curr_date)}_{timestamp(next_date)}_{str(uuid.uuid4()).split('-')[0]}"
        raw_file_name = f"{file_name}.json.gz"
        raw_path = params.out_dir / raw_file_name

        version_response = client.get("/api/0/version")
        version = version_response.json()["version"]

        with (
            client.stream(
                "GET",
                "/api/0/locations",
                params=api_params,
                headers=headers,
            ) as http_stream,
            gzip.open(raw_path, "wb") as out,
        ):
            for chunk in http_stream.iter_bytes():
                out.write(chunk)

        write_meta_file(
            out_dir=params.out_dir,
            window_start=curr_date,
            window_end=next_date,
            service_version=version,
            extract_start=extract_start,
            file_name=file_name,
        )

        last_request_date = next_date
        curr_date = next_date
        if days_left == 0:
            break

    return last_request_date
