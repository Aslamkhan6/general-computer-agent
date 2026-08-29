from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel, Field


class EventType(str, Enum):
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    
    STEP_STARTED = "STEP_STARTED"
    STEP_EXECUTED = "STEP_EXECUTED"
    STEP_OBSERVED = "STEP_OBSERVED"
    STEP_VERIFIED = "STEP_VERIFIED"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"


class Event(BaseModel):
    event_type: EventType
    task_id: str
    step_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class EventBus:
    def __init__(self):
        self._listeners: list[Callable[[Event], None]] = []

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[Event], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def publish(self, event: Event) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:
                print(f"[EventBus] Error notifying listener {listener}: {exc}")
