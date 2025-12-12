# owntracks-recorder

A **Lomnia plugin** to extract and transform data from an [OwnTracks Recorder](https://github.com/owntracks/recorder) server instance.

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

| Variable           | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| `OWNTRACKS_USER`   | Username configured on the OwnTracks Recorder server.                             |
| `OWNTRACKS_DEVICE` | Device identifier on the recorder server.                                         |
| `OWNTRACKS_URL`    | Base URL of the OwnTracks Recorder instance (e.g. `http://192.168.100.100:8083`). |

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
OWNTRACKS_USER=owntracks
OWNTRACKS_DEVICE=shiba
OWNTRACKS_URL=http://192.168.40.37:8083

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
