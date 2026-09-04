from typing import Any
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.recovery.manager import RecoveryEngine
from .base import BaseTool

_recovery_engine = RecoveryEngine()


class GetRecoveryHistoryTool(BaseTool):
    name = "get_recovery_history"
    description = "Retrieve failure logs and recovery attempt history."
    risk_level = RiskLevel.LOW
    parameters = {"task_id": "string (optional)"}

    def execute(self, task_id: str | None = None) -> ActionResult:
        try:
            if task_id:
                records = _recovery_engine.history.get_task_history(task_id)
            else:
                records = _recovery_engine.history.get_all_records()
            return ActionResult(status=ActionStatus.SUCCESS, output={"records_count": len(records), "records": [r.model_dump() for r in records]})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetCircuitBreakerStatusTool(BaseTool):
    name = "get_circuit_breaker_status"
    description = "Check circuit breaker status for a specific step ID."
    risk_level = RiskLevel.LOW
    parameters = {"step_id": "string"}

    def execute(self, step_id: str) -> ActionResult:
        try:
            tripped = _recovery_engine.circuit_breaker.is_tripped(step_id)
            return ActionResult(status=ActionStatus.SUCCESS, output={"step_id": step_id, "is_tripped": tripped})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class TriggerRollbackTool(BaseTool):
    name = "trigger_rollback"
    description = "Execute compensating inverse actions for partial task step execution."
    risk_level = RiskLevel.HIGH
    parameters = {"path": "string", "tool_name": "string"}

    def execute(self, path: str, tool_name: str = "create_directory") -> ActionResult:
        try:
            from app.core.state import TaskStep
            dummy_step = TaskStep(id="rollback-step", description="Rollback", tool_name=tool_name, input_data={"path": path})
            res = _recovery_engine.rollback_engine.rollback_step(dummy_step)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
