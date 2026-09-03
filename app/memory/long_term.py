from typing import Any
from .models import Memory, MemoryType
from .storage import MemoryStorage


class LongTermMemory:
    """Manages persistent long-term memories across application sessions."""

    def __init__(self, storage: MemoryStorage | None = None):
        self.storage = storage or MemoryStorage()

    def add(self, memory: Memory) -> None:
        memory.persistent = True
        self.storage.save(memory)

    def get_by_id(self, memory_id: str) -> Memory | None:
        mem = self.storage.get(memory_id)
        if mem:
            mem.touch()
            self.storage.save(mem)
        return mem

    def get_by_type(self, memory_type: MemoryType) -> list[Memory]:
        all_mems = self.storage.load_all()
        return [m for m in all_mems if m.type == memory_type]

    def all_memories(self) -> list[Memory]:
        return self.storage.load_all()

    def delete(self, memory_id: str) -> bool:
        return self.storage.delete(memory_id)
