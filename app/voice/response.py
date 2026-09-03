from typing import Any
from app.core.enums import TaskStatus
from app.core.state import AgentTask


class VoiceResponseManager:
    """Converts structured Agent Core results into natural spoken text responses."""

    def format_task_response(self, task: AgentTask) -> str:
        if task.status == TaskStatus.COMPLETED:
            if task.final_result and isinstance(task.final_result, dict):
                steps = task.final_result.get("steps_completed", len(task.steps))
                return f"Task completed successfully. All {steps} steps executed and verified."
            return "Task completed successfully."
        elif task.status == TaskStatus.FAILED:
            err = task.error or "Unknown execution error."
            return f"I couldn't complete the task. {err}"
        elif task.status == TaskStatus.PAUSED:
            return "The task has been paused waiting for your input or confirmation."
        else:
            return f"Task status is currently {task.status.value}."

    def format_error_response(self, error_message: str) -> str:
        return f"Voice system error: {error_message}"

    def format_confirmation_request(self, action_description: str) -> str:
        return f"This action will {action_description}. Do you want me to proceed?"
