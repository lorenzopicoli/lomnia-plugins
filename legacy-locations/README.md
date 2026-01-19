# Legacy Locations

A **Lomnia plugin** to extract and transform data from an old instance of Lomnia.

When I started developing Lomnia there were two sources of location data and they weren't properly backed up or imported

Export old data from the "raw" column:

```
\COPY (
   SELECT jsonb_build_object(
     'table', 'locations',
     'row_id', id,
     'timezone', timezone,
     'import_job_id', import_job_id,
     'recorded_at', location_fix,
     'raw', CASE
       WHEN jsonb_typeof(raw_data) = 'string'
         THEN (raw_data #>> '{}')::jsonb
       ELSE raw_data
     END
   )
   FROM locations
   where source = 'sqlite_locations'
   ORDER BY id
 ) TO '/tmp/locations_raw.jsonl';
```

```
➜  lomnia-ingester git:(main) ✗ sudo docker cp 549ff2c72be5:/tmp/locations_raw.jsonl ./locations_raw.jsonl
```

```
gzip locations_raw.jsonl
```

The jsonlines will have more than one type of record. The initial one from my own server:

```
{
  "raw": {
    "id": 1000014,
    "radius": null,
    "battery": 37,
    "tagName": null,
    "accuracy": 3,
    "altitude": 120,
    "latitude": 43,
    "velocity": 0,
    "wifiSSID": null,
    "longitude": 3,
    "timestamp": "2024-07-04T11:17:09.000Z",
    "trackerId": "ba",
    "wifiBSSID": null,
    "triggerType": null,
    "batteryStatus": 1,
    "monitoringMode": 2,
    "pointOfInterest": null,
    "connectionStatus": "m",
    "courseOverGround": null,
    "verticalAccuracy": 3,
    "regionCurrentlyIn": null,
    "barometricPressure": null,
    "messageCreationTime": "2024-07-04T11:17:09.000Z",
    "originalPublishTopic": "owntracks/user/shiba",
    "regionIdsCurrentlyIn": null
  },
  "table": "locations",
  "row_id": 1000023,
  "timezone": "Europe/Paris",
  "recorded_at": "2024-07-04T11:17:09+00:00",
  "import_job_id": 657
}
```

And another one from when I transitioned to owntracks recorder:

```
{
  "raw": {
    "m": 2,
    "bs": 1,
    "_id": "2ef93a57",
    "acc": 12,
    "alt": 26,
    "cog": 0,
    "lat": 45,
    "lon": -73,
    "tid": "ba",
    "tst": 1757979198,
    "vac": 0,
    "vel": 0,
    "SSID": "Anya - Secure",
    "batt": 32,
    "conn": "w",
    "BSSID": "06:ec:da:ae:0c:de",
    "_http": true,
    "_type": "location",
    "ghash": "f25ehek",
    "topic": "owntracks/user/shiba",
    "isorcv": "2025-09-15T23:33:18Z",
    "isotst": "2025-09-15T23:33:18Z",
    "source": "fused",
    "tzname": "America/Toronto",
    "disptst": "2025-09-15 23:33:18",
    "isolocal": "2025-09-15T19:33:18-0400",
    "created_at": 1757979198
  },
  "table": "locations",
  "row_id": 11896408,
  "timezone": "Europe/Paris",
  "recorded_at": "2025-09-15T23:33:18+00:00",
  "import_job_id": 2853
}
```

## Overview

This plugin operates in two phases:

1. **Extract** – Downloads raw JSON responses from the OwnTracks Recorder API.
2. **Transform** – Normalizes the extracted data into a compressed JSONL file containing:
   - `locations`
   - `devices`
   - `device_statuses`

## Environment Variables

The extractor requires the following environment variables.
These are typically defined in the plugin's `env` section in your YAML configuration, but you can also define it in a `.env` file.

### Required

| Variable            | Description                                                   |
| ------------------- | ------------------------------------------------------------- |
| `DEVICE`            | (Required) The device ID for all entries.                     |
| `SKIP_SCHEMA_CHECK` | (Optional) Skip checking for the schema. Improves performance |

### Optional (Local Schemas)

Used by the transformer to validate output.
If not set, Lomnia defaults are used.

| Variable                     | Description                             |
| ---------------------------- | --------------------------------------- |
| `LOCATION_SCHEMA_LOCAL`      | Path to the `Location` JSON schema.     |
| `DEVICE_SCHEMA_LOCAL`        | Path to the `Device` JSON schema.       |
| `DEVICE_STATUS_SCHEMA_LOCAL` | Path to the `DeviceStatus` JSON schema. |

Examples:

```
DEVICE=shiba

LOCATION_SCHEMA_LOCAL=/path/to/Location.schema.json
DEVICE_SCHEMA_LOCAL=/path/to/Device.schema.json
DEVICE_STATUS_SCHEMA_LOCAL=/path/to/DeviceStatus.schema.json
```

## Commands

### Extract

Produces multiple JSON files containing raw API responses.

```
uv run extract --start_date <unix_timestamp> --out_dir <output_directory>
```

**Params:**

| Parameter      | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `--start_date` | Unix timestamp (seconds) to start fetching location updates. |
| `--out_dir`    | Directory where raw response files should be written.        |
| `--in_dir`     | Directory containing files to be extracted.                  |

---

### Transform

Reads the raw JSON files and produces a single compressed JSONL file with normalized data.

```
uv run transform --in_dir <raw_input_directory> --out_dir <canonical_output_directory>
```

**Params:**

| Parameter   | Description                                          |
| ----------- | ---------------------------------------------------- |
| `--in_dir`  | Directory containing files created by the extractor. |
| `--out_dir` | Directory where canonical output should be written.  |

## Getting started with your project

### 1. Clone the repo

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git clone git@github.com:lorenzopicoli/lomnia-plugins.git
```

### 2. Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file

### 3. Run the pre-commit hooks

Initially, the CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
uv run pre-commit run -a
```

### 4. Commit the changes

Lastly, commit the changes made by the two steps above to your repository.

```bash
git add .
git commit -m 'Fix formatting issues'
git push origin main
```
