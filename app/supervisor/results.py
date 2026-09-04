from typing import Any
from .models import AgentResult, AgentStatus, SubTask


class ResultManager:
    """Collects and aggregates subtask execution results from worker agents."""

    def __init__(self):
        self._results: dict[str, list[AgentResult]] = {}

    def add_result(self, result: AgentResult) -> None:
        if result.task_id not in self._results:
            self._results[result.task_id] = []
        self._results[result.task_id].append(result)

    def get_results_for_task(self, task_id: str) -> list[AgentResult]:
        return self._results.get(task_id, [])

    def aggregate(self, task_id: str, subtasks: list[SubTask]) -> dict[str, Any]:
        results = self.get_results_for_task(task_id)
        all_completed = len(results) == len(subtasks) and all(r.status == AgentStatus.COMPLETED for r in results)
        all_verified = all(r.verified for r in results)

        combined_outputs = {}
        combined_artifacts = []
        for r in results:
            combined_outputs[r.subtask_id] = r.output
            combined_artifacts.extend(r.artifacts)

        return {
            "task_id": task_id,
            "status": AgentStatus.COMPLETED if (all_completed and all_verified) else AgentStatus.FAILED,
            "subtasks_total": len(subtasks),
            "subtasks_completed": len(results),
            "verified": all_verified,
            "outputs": combined_outputs,
            "artifacts": list(set(combined_artifacts)),
        }
