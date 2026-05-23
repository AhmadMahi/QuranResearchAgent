import re
from typing import Tuple

_BLOCKED = [
    "violence", "terrorism", "explicit content", "illegal activities",
    "weapons manufacture", "drug synthesis", "hate speech", "child abuse",
]

_MAX_LEN = 500
_MIN_LEN = 3


def validate_input(topic: str, city: str = "", country: str = "") -> Tuple[bool, str]:
    topic = topic.strip()

    if len(topic) < _MIN_LEN:
        return False, "Topic is too short — please use at least 3 characters."

    if len(topic) > _MAX_LEN:
        return False, f"Topic is too long — please keep it under {_MAX_LEN} characters."

    lower = topic.lower()
    for word in _BLOCKED:
        if word in lower:
            return False, "Topic contains restricted content. Please choose a different subject."

    if re.search(r"[<>{}]|javascript:|data:|<script", topic, re.IGNORECASE):
        return False, "Topic contains invalid characters."

    return True, "ok"


def validate_output(report: str) -> Tuple[bool, str]:
    if not report or len(report.strip()) < 80:
        return False, "Generated report is unexpectedly short."
    if len(report) > 60_000:
        return False, "Generated report is unexpectedly long."
    return True, "ok"


def sanitize(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)       # strip HTML
    text = re.sub(r"\s+", " ", text).strip()  # collapse whitespace
    return text
