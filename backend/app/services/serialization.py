import json
from typing import Any


def dumps_list(values: list[str] | None) -> str:
    return json.dumps(values or [], ensure_ascii=False)


def loads_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    try:
        decoded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return [part.strip() for part in str(value).split(",") if part.strip()]
    return decoded if isinstance(decoded, list) else []
