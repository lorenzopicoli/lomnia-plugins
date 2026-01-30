import argparse
from pathlib import Path

from dotenv import load_dotenv

from obsidian_habits.transform.run import run_transform
from obsidian_habits.transform.schemas import get_schemas

load_dotenv()


def transform():
    parser = argparse.ArgumentParser()

    parser.add_argument("--out_dir", required=True, type=Path, help="Output directory path")
    parser.add_argument("--in_dir", required=True, type=Path, help="Input directory path")
    args = parser.parse_args()

    # env = EnvVars()
    schemas = get_schemas()

    print(f"In Dir: {args.in_dir}")
    print(f"Out Dir: {args.out_dir}")
    # print(f"Env vars: {env}")
    print(f"Is skipping schemas: {schemas.skip_schema_check}")

    run_transform(out_dir=args.out_dir, in_dir=args.in_dir, schemas=schemas)

    print("Done transforming!")


def main():
    transform()


if __name__ == "__main__":
    main()
