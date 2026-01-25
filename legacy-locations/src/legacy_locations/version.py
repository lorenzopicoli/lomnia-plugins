from importlib.metadata import PackageNotFoundError, version

from legacy_locations.config import PACKAGE_NAME


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"
