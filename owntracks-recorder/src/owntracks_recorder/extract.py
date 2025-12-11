import argparse
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple

import httpx


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


def write_locations(client: httpx.Client, user: str, device: str, start_date: datetime, out_dir: Path):
    params = {
        "user": user,
        "device": device
    }
    curr_date = start_date
    last_request_date: date | None = None
    while curr_date < datetime.now(tz=timezone.utc) - timedelta(seconds=10):
        extra_day = curr_date + timedelta(days=1)
        next_date = extra_day if extra_day < datetime.now(
            tz=timezone.utc) else datetime.now(tz=timezone.utc)
        headers = {
            "X-Limit-From": curr_date.isoformat(),
            "X-Limit-To": next_date.isoformat()
        }
        print(
            f"Fetching data from {headers['X-Limit-From']} to {headers['X-Limit-To']}")
        last_request_date = next_date
        file_name = os.path.join(
            out_dir, f"owntracks_{curr_date.timestamp()}_{next_date.timestamp()}.json")
        with client.stream("GET",
                           "/api/0/locations",
                           params=params,
                           headers=headers) as http_stream, open(file_name, "wb") as out:
            for data in http_stream.iter_bytes():
                out.write(data)

        curr_date = next_date

    return last_request_date


def extract() -> datetime:
    args = parse_extract_args()
    user = os.environ.get('OWNTRACKS_USER', None)
    device = os.environ.get('OWNTRACKS_DEVICE', None)
    if user is None:
        raise MissingEnvVar("OWNTRACKS_USER")
    if device is None:
        raise MissingEnvVar("OWNTRACKS_DEVICE")

    last_request: date | None = None
    with httpx.Client(base_url="http://192.168.40.37:8083", timeout=30.0) as client:
        last_request = write_locations(client, user=user, device=device,
                                       start_date=args.start_date, out_dir=args.out_dir)

    if last_request is None:
        raise FailedToExtract("NO_REQUEST_VALUE")
    return last_request


def main():
    extract()


if __name__ == "__main__":
    main()
