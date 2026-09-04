from typing import Any
from .models import AgentStatus, SubTask, WorkerAgentInfo
from .registry import AgentRegistry


class TaskDispatcher:
    """Dispatches subtasks to candidate worker agents based on role and capabilities."""

    def __init__(self, registry: AgentRegistry | None = None):
        self.registry = registry or AgentRegistry()

    def dispatch(self, subtask: SubTask) -> WorkerAgentInfo:
        worker = self.registry.find_best_agent(
            required_capabilities=subtask.required_capabilities,
            role_hint=subtask.assigned_role,
        )
        if not worker:
            raise RuntimeError(f"No suitable worker agent found for subtask '{subtask.id}' (Role: {subtask.assigned_role}).")

        worker.status = AgentStatus.ASSIGNED
        worker.current_task_id = subtask.id
        subtask.status = AgentStatus.ASSIGNED
        return worker
