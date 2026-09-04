from typing import Any


class ResourceManager:
    """Controls resource locking and prevents file/directory conflict race conditions among worker agents."""

    def __init__(self):
        self._locks: dict[str, str] = {}  # resource_path -> agent_id

    def acquire_lock(self, resource_path: str, agent_id: str) -> tuple[bool, str]:
        res_norm = resource_path.lower()
        if res_norm in self._locks and self._locks[res_norm] != agent_id:
            locked_by = self._locks[res_norm]
            return False, f"Resource '{resource_path}' is locked by agent '{locked_by}'."

        self._locks[res_norm] = agent_id
        return True, f"Resource '{resource_path}' locked by agent '{agent_id}'."

    def release_lock(self, resource_path: str, agent_id: str) -> bool:
        res_norm = resource_path.lower()
        if self._locks.get(res_norm) == agent_id:
            del self._locks[res_norm]
            return True
        return False

    def is_locked(self, resource_path: str) -> bool:
        return resource_path.lower() in self._locks
