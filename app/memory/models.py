from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class MemoryType(str, Enum):
    USER_PREFERENCE = "USER_PREFERENCE"
    USER_FACT = "USER_FACT"
    PROJECT_CONTEXT = "PROJECT_CONTEXT"
    TASK_HISTORY = "TASK_HISTORY"
    ENVIRONMENT = "ENVIRONMENT"
    LEARNED_PATTERN = "LEARNED_PATTERN"
    IMPORTANT_EVENT = "IMPORTANT_EVENT"


class MemorySource(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"


class Memory(BaseModel):
    id: str = Field(default_factory=lambda: f"mem-{uuid.uuid4().hex[:8]}")
    content: str
    type: MemoryType = MemoryType.TASK_HISTORY
    source: MemorySource = MemorySource.USER
    importance: float = 0.5
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    expiration: datetime | None = None
    persistent: bool = False

    def touch(self) -> None:
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1
