import json
import os
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import sleep

import garth

from garmin.config import PLUGIN_NAME
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


def run_extract(params: ExtractionParams):
    extract_start = datetime.now(timezone.utc)
    garth.login(params.email, params.password)
    file_id = str(uuid.uuid4()).split("-")[0]
    day_delay = 2

    curr_date = params.start_date
    while curr_date < datetime.now(tz=timezone.utc) - timedelta(days=day_delay):
        fetch_data_for_day(params, curr_date, file_id)
        curr_date = curr_date + timedelta(days=1)
        sleep(1)

    file_name = f"{PLUGIN_NAME}_{file_id}"
    write_meta_file(
        out_dir=params.out_dir,
        file_name=file_name,
        extract_start=extract_start,
    )


def fetch_data_for_day(params: ExtractionParams, current_day: datetime, file_id: str):
    day = current_day.strftime("%Y-%m-%d")
    print(f"Fetching day {day}")

    prefix = f"{day}_{file_id}"
    name = params.username

    sleep_data_file = params.out_dir / f"{prefix}_daily_sleep_data.json"
    rh_file = params.out_dir / f"{prefix}_daily_rh.json"
    weight_file = params.out_dir / f"{prefix}_weight_date_range.json"

    query_params = {"date": day, "nonSleepBufferMinutes": 60}
    sleep_data = garth.connectapi(
        f"{garmin_connect_sleep_daily_url}/{name}",
        params=query_params,
    )
    sleep_data_file.write_text(json.dumps(sleep_data, indent=2))

    query_params = {"date": day}
    rh_data = garth.connectapi(
        garmin_connect_daily_heart_rate,
        params=query_params,
    )
    rh_file.write_text(json.dumps(rh_data, indent=2))

    query_params = {"startDate": day, "endDate": day}
    weight_data = garth.connectapi(
        garmin_connect_weight_url,
        params=query_params,
    )
    weight_file.write_text(json.dumps(weight_data, indent=2))

    client = garth.Client()
    activities = garth.Activity.list(limit=10, start=0)

    for activity in activities:
        result = client.get(
            "connectapi",
            f"{garmin_connect_download_service_url}/activity/{activity.activity_id}",
        )

        activity_zip = params.out_dir / f"{prefix}_activity_{activity.activity_id}.zip"

        with open(activity_zip, "wb") as file:
            for chunk in result:
                file.write(chunk)

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(activity_zip, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            for extracted in Path(tmpdir).iterdir():
                if extracted.is_file():
                    new_name = f"{prefix}_{extracted.name}"
                    shutil.move(str(extracted), params.out_dir / new_name)

        os.remove(activity_zip)
