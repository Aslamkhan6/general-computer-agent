from typing import Any
from .models import SharedTaskContext, SubTask


class SharedTaskContextManager:
    """Manages shared task goals, artifacts, subtask outputs, and verification results across worker agents."""

    def __init__(self):
        self._contexts: dict[str, dict[str, Any]] = {}

    def init_context(self, task_id: str, goal: str) -> dict[str, Any]:
        ctx = {
            "task_id": task_id,
            "goal": goal,
            "completed_subtasks": [],
            "subtask_outputs": {},
            "shared_artifacts": [],
            "errors": [],
        }
        self._contexts[task_id] = ctx
        return ctx

    def get_context(self, task_id: str) -> dict[str, Any]:
        if task_id not in self._contexts:
            self.init_context(task_id, "Default Goal")
        return self._contexts[task_id]

    def record_subtask_result(self, task_id: str, subtask_id: str, output: dict[str, Any], artifacts: list[str] | None = None) -> None:
        ctx = self.get_context(task_id)
        if subtask_id not in ctx["completed_subtasks"]:
            ctx["completed_subtasks"].append(subtask_id)
        ctx["subtask_outputs"][subtask_id] = output
        if artifacts:
            for art in artifacts:
                if art not in ctx["shared_artifacts"]:
                    ctx["shared_artifacts"].append(art)
