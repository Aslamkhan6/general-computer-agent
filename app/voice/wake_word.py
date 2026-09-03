import re
from dataclasses import dataclass
from typing import Any


@dataclass
class WakeWordDetectionResult:
    detected: bool
    wake_phrase: str | None = None
    remaining_text: str = ""


class WakeWordDetector:
    """Lightweight wake word / keyword detector for hands-free activation."""

    DEFAULT_WAKE_WORDS = [
        "hey computer",
        "hey agent",
        "computer",
        "assistant",
    ]

    def __init__(self, wake_words: list[str] | None = None):
        self.wake_words = [w.lower() for w in (wake_words or self.DEFAULT_WAKE_WORDS)]

    def detect(self, text: str) -> WakeWordDetectionResult:
        if not text:
            return WakeWordDetectionResult(detected=False)

        lower_text = text.lower()
        for phrase in self.wake_words:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            match = re.search(pattern, lower_text)
            if match:
                end_pos = match.end()
                remaining = text[end_pos:].strip(",. ")
                return WakeWordDetectionResult(
                    detected=True,
                    wake_phrase=phrase,
                    remaining_text=remaining,
                )

        return WakeWordDetectionResult(detected=False, remaining_text=text)
