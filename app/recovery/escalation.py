from typing import Any
from .models import FailureCategory, FailureReport


class EscalationInterface:
    """Handles human escalation when automated recovery cannot safely proceed."""

    def escalate(self, report: FailureReport, reason: str = "Unrecoverable failure threshold reached") -> dict[str, Any]:
        return {
            "escalated": True,
            "task_id": report.task_id,
            "step_id": report.step_id,
            "category": report.category.value,
            "error_message": report.error_message,
            "reason": reason,
            "action_required": "Human intervention or explicit authorization required.",
        }
