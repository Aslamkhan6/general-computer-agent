import os
import shutil
from typing import Any
from app.core.state import AgentTask, TaskStep


class RollbackEngine:
    """Executes compensating inverse actions to safely rollback partial execution side-effects."""

    def rollback_step(self, step: TaskStep) -> dict[str, Any]:
        tool = step.tool_name
        path = step.input_data.get("path")
        rolled_back = False
        details = ""

        if path and os.path.exists(path):
            try:
                if tool in ("create_file", "write_file"):
                    os.remove(path)
                    rolled_back = True
                    details = f"Deleted file '{path}'"
                elif tool == "create_directory":
                    shutil.rmtree(path, ignore_errors=True)
                    rolled_back = True
                    details = f"Deleted directory '{path}'"
            except Exception as exc:
                details = f"Failed to delete '{path}': {exc}"

        return {
            "step_id": step.id,
            "tool_name": tool,
            "rolled_back": rolled_back,
            "details": details or "No rollback action required.",
        }

    def rollback_task(self, task: AgentTask) -> list[dict[str, Any]]:
        results = []
        for step in reversed(task.steps):
            if step.status != "PENDING":
                res = self.rollback_step(step)
                results.append(res)
        return results
