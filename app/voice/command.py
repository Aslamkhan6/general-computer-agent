import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessedVoiceCommand:
    raw_transcript: str
    cleaned_command: str
    is_cancellation: bool = False
    is_empty: bool = False
    confidence: float = 1.0


class VoiceCommandProcessor:
    """Cleans raw transcriptions, removes filler words, and prepares intent string for Agent Core."""

    FILLER_WORDS = [
        r"\buhh?\b",
        r"\bumm?\b",
        r"\bokay computer\b",
        r"\bplease\b",
        r"\bhey agent\b",
        r"\bhey computer\b",
        r"\bcan you\b",
        r"\bcould you\b",
        r"\bwould you mind\b",
    ]

    CANCELLATION_PHRASES = [
        "cancel",
        "never mind",
        "stop",
        "abort",
        "forget it",
    ]

    def process(self, raw_transcript: str, confidence: float = 1.0) -> ProcessedVoiceCommand:
        text = raw_transcript.strip()
        if not text:
            return ProcessedVoiceCommand(
                raw_transcript=raw_transcript,
                cleaned_command="",
                is_cancellation=False,
                is_empty=True,
                confidence=0.0,
            )

        # Check cancellation
        lower_text = text.lower()
        for cancel_word in self.CANCELLATION_PHRASES:
            if cancel_word in lower_text:
                return ProcessedVoiceCommand(
                    raw_transcript=raw_transcript,
                    cleaned_command="cancel",
                    is_cancellation=True,
                    is_empty=False,
                    confidence=confidence,
                )

        # Clean filler words
        cleaned = lower_text
        for filler in self.FILLER_WORDS:
            cleaned = re.sub(filler, "", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return ProcessedVoiceCommand(
            raw_transcript=raw_transcript,
            cleaned_command=cleaned or text,
            is_cancellation=False,
            is_empty=False,
            confidence=confidence,
        )
