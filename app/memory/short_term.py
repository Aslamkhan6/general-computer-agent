from datetime import datetime, timezone
from typing import Any
from .models import Memory, MemorySource, MemoryType


class ShortTermMemory:
    """Manages active session context, recent conversation turns, and transient variables."""

    def __init__(self, session_id: str = "session-default"):
        self.session_id = session_id
        self.current_context: dict[str, Any] = {
            "last_directory": None,
            "last_created_file": None,
            "last_operation": None,
            "active_project": None,
        }
        self._recent_memories: list[Memory] = []

    def add_event(self, content: str, memory_type: MemoryType = MemoryType.TASK_HISTORY, metadata: dict[str, Any] | None = None) -> Memory:
        mem = Memory(
            content=content,
            type=memory_type,
            source=MemorySource.AGENT,
            importance=0.4,
            persistent=False,
            metadata=metadata or {},
        )
        self._recent_memories.append(mem)

        # Update transient variables heuristics
        if "directory" in content.lower() or "folder" in content.lower():
            if metadata and "path" in metadata:
                self.current_context["last_directory"] = metadata["path"]
            self.current_context["last_operation"] = "create_directory"
        elif "file" in content.lower():
            if metadata and "path" in metadata:
                self.current_context["last_created_file"] = metadata["path"]
            self.current_context["last_operation"] = "create_file"

        return mem

    def update_context(self, key: str, value: Any) -> None:
        self.current_context[key] = value

    def get_context(self) -> dict[str, Any]:
        return dict(self.current_context)

    def get_recent(self, limit: int = 5) -> list[Memory]:
        return self._recent_memories[-limit:]

    def clear(self) -> None:
        self.current_context.clear()
        self._recent_memories.clear()
