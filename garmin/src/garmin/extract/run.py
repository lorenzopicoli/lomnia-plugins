import json
import os
import shutil
import tarfile
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import sleep

import garth

from garmin.config import ACTIVITY_FOLDER, DEVICE_FOLDER, HR_FOLDER, PLUGIN_NAME, SLEEP_FOLDER, WEIGHT_FOLDER
from garmin.extract.meta import write_meta_file


@dataclass
class ExtractionParams:
    start_date: datetime
    out_dir: Path
    in_dir: Path

    username: str
    email: str
    password: str


garmin_connect_sleep_daily_url = "/wellness-service/wellness/dailySleepData"
garmin_connect_daily_heart_rate = "/wellness-service/wellness/dailyHeartRate"
garmin_connect_weight_url = "/weight-service/weight/dateRange"
garmin_connect_download_service_url = "/download-service/files"
garmin_connect_device_url = "/web-gateway/device-info/primary-training-device"


def run_extract(params: ExtractionParams):
    extract_start = datetime.now(timezone.utc)
    garth.login(params.email, params.password)
    file_id = str(uuid.uuid4()).split("-")[0]
    day_delay = 2

    curr_date = params.start_date
    fetch_device_data(params, file_id)
    while curr_date < datetime.now(tz=timezone.utc) - timedelta(days=day_delay):
        fetch_data_for_day(params, curr_date, file_id)
        curr_date = curr_date + timedelta(days=1)
        sleep(1)

    start_day = params.start_date.strftime("%Y-%m-%d")
    end_day = curr_date.strftime("%Y-%m-%d")
    final_file_name = f"{PLUGIN_NAME}_{start_day}_{end_day}_{file_id}"
    archive_in_place(str(params.out_dir), final_file_name)
    write_meta_file(
        out_dir=params.out_dir,
        file_name=final_file_name,
        extract_start=extract_start,
    )


def fetch_device_data(params: ExtractionParams, file_id: str):
    device_data_file = params.out_dir / DEVICE_FOLDER / f"{file_id}_device_data.json"
    device_data_file.parent.mkdir(parents=True, exist_ok=True)
    device_data = garth.connectapi(
        f"{garmin_connect_device_url}",
    )
    device_data_file.write_text(json.dumps(device_data, indent=2))


def fetch_data_for_day(params: ExtractionParams, current_day: datetime, file_id: str):
    day = current_day.strftime("%Y-%m-%d")
    print(f"Fetching day {day}")

    prefix = f"{day}_{file_id}"
    name = params.username

    sleep_data_file = params.out_dir / SLEEP_FOLDER / f"{prefix}_daily_sleep_data.json"
    hr_file = params.out_dir / HR_FOLDER / f"{prefix}_daily_hr.json"
    weight_file = params.out_dir / WEIGHT_FOLDER / f"{prefix}_weight_date_range.json"

    sleep_data_file.parent.mkdir(parents=True, exist_ok=True)
    hr_file.parent.mkdir(parents=True, exist_ok=True)
    weight_file.parent.mkdir(parents=True, exist_ok=True)

    query_params = {"date": day, "nonSleepBufferMinutes": 60}
    sleep_data = garth.connectapi(
        f"{garmin_connect_sleep_daily_url}/{name}",
        params=query_params,
    )
    sleep_data_file.write_text(json.dumps(sleep_data, indent=2))

    query_params = {"date": day}
    hr_data = garth.connectapi(
        garmin_connect_daily_heart_rate,
        params=query_params,
    )
    hr_file.write_text(json.dumps(hr_data, indent=2))

    query_params = {"startDate": day, "endDate": day}
    weight_data = garth.connectapi(
        garmin_connect_weight_url,
        params=query_params,
    )
    weight_file.write_text(json.dumps(weight_data, indent=2))

    activity_dir = params.out_dir / ACTIVITY_FOLDER
    activity_dir.mkdir(parents=True, exist_ok=True)

    client = garth.Client()
    activities = garth.Activity.list(limit=10, start=0)

    for activity in activities:
        result = client.get(
            "connectapi",
            f"{garmin_connect_download_service_url}/activity/{activity.activity_id}",
        )

        activity_zip = activity_dir / f"{prefix}_activity_{activity.activity_id}.zip"

        with open(activity_zip, "wb") as file:
            for chunk in result:
                file.write(chunk)

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(activity_zip, "r") as zip_ref:
                zip_ref.extractall(tmpdir)  # noqa: S202

            for extracted in Path(tmpdir).iterdir():
                if extracted.is_file():
                    new_name = f"{prefix}_{extracted.name}"
                    shutil.move(str(extracted), activity_dir / new_name)

        os.remove(activity_zip)


def archive_in_place(source_dir: str, file_name: str):
    source_path = Path(source_dir)
    archive_path = source_path / f"{file_name}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        for item in source_path.iterdir():
            if item == archive_path:
                continue
            tar.add(item, arcname=item.name)

    for item in source_path.iterdir():
        if item != archive_path:
            if item.is_file():
                item.unlink()
            else:
                import shutil

                shutil.rmtree(item)
