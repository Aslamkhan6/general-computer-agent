from typing import Any
from .models import AgentStatus, SubTask


class TaskScheduler:
    """Manages subtask dependency graphs and parallel/sequential execution schedules."""

    def get_executable_subtasks(self, subtasks: list[SubTask], completed_subtask_ids: set[str]) -> list[SubTask]:
        executable = []
        for st in subtasks:
            if st.status in (AgentStatus.COMPLETED, AgentStatus.RUNNING, AgentStatus.ASSIGNED):
                continue
            # Check if all dependencies are satisfied
            deps_satisfied = all(dep_id in completed_subtask_ids for dep_id in st.dependencies)
            if deps_satisfied:
                executable.append(st)
        return executable

    def is_all_completed(self, subtasks: list[SubTask]) -> bool:
        return all(st.status == AgentStatus.COMPLETED for st in subtasks)
