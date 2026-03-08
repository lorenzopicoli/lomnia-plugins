from typing import TypeVar

T = TypeVar("T")


def remove_none_values(d: dict[str, T]) -> dict[str, T]:
    return {k: v for k, v in d.items() if v is not None}
