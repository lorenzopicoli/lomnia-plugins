from importlib.metadata import PackageNotFoundError, version

from obsidian_habits.config import PACKAGE_NAME


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"
