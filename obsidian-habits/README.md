# Obsidian Habits

A **Lomnia plugin** to extract and transform habit data from a JSON file that I exported my daily notes into

## Environment Variables

The extractor requires the following environment variables.
These are typically defined in the plugin's `env` section in your YAML configuration, but you can also define it in a `.env` file.

### Required

| Variable            | Description                                                   |
| ------------------- | ------------------------------------------------------------- |
| `SKIP_SCHEMA_CHECK` | (Optional) Skip checking for the schema. Improves performance |

### Optional (Local Schemas)

Used by the transformer to validate output.
If not set, Lomnia defaults are used.

| Variable                     | Description                             |
| ---------------------------- | --------------------------------------- |
| `HABIT_SCHEMA_LOCAL`      | Path to the `Location` JSON schema.     |

``

## Commands

### Extract

Produces a gzip file for the latest json in the in-dir

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

Reads the json file and produces a single compressed JSONL file with normalized data.

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
