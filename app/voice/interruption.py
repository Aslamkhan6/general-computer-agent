import re
from dataclasses import dataclass


@dataclass
class InterruptionResult:
    interrupted: bool
    trigger_word: str | None = None


class VoiceInterruptionHandler:
    """Handles voice barge-in and interruption detection."""

    INTERRUPT_KEYWORDS = [
        "stop",
        "cancel",
        "shut up",
        "wait",
        "hold on",
        "pause",
        "never mind",
    ]

    def check_interruption(self, transcript: str) -> InterruptionResult:
        if not transcript:
            return InterruptionResult(interrupted=False)

        lower = transcript.lower()
        for word in self.INTERRUPT_KEYWORDS:
            pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, lower):
                return InterruptionResult(interrupted=True, trigger_word=word)

        return InterruptionResult(interrupted=False)
