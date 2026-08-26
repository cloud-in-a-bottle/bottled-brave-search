"""Narrowing helpers for `json.loads` output, so parsing never needs `Any`."""

from collections.abc import Mapping
from collections.abc import Sequence

JsonObject = Mapping[str, object]


def as_object(value: object) -> JsonObject | None:
    return value if isinstance(value, Mapping) else None


def get_object(obj: JsonObject, key: str) -> JsonObject | None:
    return as_object(obj.get(key))


def get_str(obj: JsonObject, key: str) -> str | None:
    value = obj.get(key)
    return value if isinstance(value, str) and value != "" else None


def get_int(obj: JsonObject, key: str) -> int | None:
    value = obj.get(key)
    # bool is an int subclass, but a boolean field is never a meaningful integer here.
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def get_bool(obj: JsonObject, key: str) -> bool:
    value = obj.get(key)
    return value if isinstance(value, bool) else False


def get_list(obj: JsonObject, key: str) -> Sequence[object]:
    value = obj.get(key)
    if isinstance(value, str) or not isinstance(value, Sequence):
        return ()
    return value


def get_objects(obj: JsonObject, key: str) -> tuple[JsonObject, ...]:
    return tuple(item for item in (as_object(entry) for entry in get_list(obj, key)) if item is not None)


def get_strs(obj: JsonObject, key: str) -> tuple[str, ...]:
    return tuple(entry for entry in get_list(obj, key) if isinstance(entry, str) and entry != "")
