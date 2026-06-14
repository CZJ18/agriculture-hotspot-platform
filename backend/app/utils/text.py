import re
from collections import Counter


def compact_text(value: str, limit: int = 1200) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    return cleaned[:limit]


def simple_keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[\w\u4e00-\u9fff]{2,}", text.lower())
    stop = {"the", "and", "for", "with", "this", "that", "from", "https", "http"}
    return [word for word, _ in Counter(w for w in words if w not in stop).most_common(limit)]
