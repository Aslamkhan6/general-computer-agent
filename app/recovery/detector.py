from typing import Any
from app.core.enums import ActionStatus, StepStatus
from app.core.state import ActionResult, TaskStep
from .models import FailureReport, FailureCategory


class FailureDetector:
    """Detects tool execution failures, verification failures, or unexpected state mismatches."""

    def detect(self, task_id: str, step: TaskStep, execution_result: ActionResult | None = None, actual_state: dict[str, Any] | None = None, verified: bool = True) -> FailureReport | None:
        if execution_result and execution_result.status != ActionStatus.SUCCESS:
            err_msg = execution_result.error or "Tool execution failed."
            return FailureReport(
                task_id=task_id,
                step_id=step.id,
                error_message=err_msg,
                category=FailureCategory.TOOL,
                details={"tool_name": step.tool_name, "input_data": step.input_data, "output": execution_result.output},
            )

        if not verified:
            return FailureReport(
                task_id=task_id,
                step_id=step.id,
                error_message="State verification failed: actual state did not match expected state.",
                category=FailureCategory.VERIFICATION,
                details={"expected": step.expected_state, "actual": actual_state},
            )

        if step.status == StepStatus.FAILED:
            return FailureReport(
                task_id=task_id,
                step_id=step.id,
                error_message=step.error or "Step failed.",
                category=FailureCategory.UNKNOWN,
                details={"tool_name": step.tool_name},
            )

        return None
