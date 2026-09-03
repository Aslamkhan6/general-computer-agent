from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class VoiceState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    RECORDING = "RECORDING"
    TRANSCRIBING = "TRANSCRIBING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


class VoiceSessionManager:
    """Manages the state lifecycle of a voice interaction session."""

    def __init__(self):
        self._state: VoiceState = VoiceState.IDLE
        self._history: list[dict[str, Any]] = []
        self._listeners: list[Callable[[VoiceState, VoiceState], None]] = []

    @property
    def current_state(self) -> VoiceState:
        return self._state

    def subscribe(self, listener: Callable[[VoiceState, VoiceState], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def transition_to(self, new_state: VoiceState, details: str | None = None) -> None:
        old_state = self._state
        self._state = new_state
        entry = {
            "from_state": old_state.value,
            "to_state": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }
        self._history.append(entry)
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)
