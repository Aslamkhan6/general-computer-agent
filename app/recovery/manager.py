from typing import Any
from app.core.state import ActionResult, TaskStep
from app.observer.base import BaseObserver
from app.planner.plan import TaskPlan
from app.planner.planner import Planner
from app.tools.executor import ToolExecutor
from app.verifier.base import BaseVerifier

from .alternative_tool import AlternativeToolEngine
from .circuit_breaker import CircuitBreaker
from .classifier import FailureClassifier
from .detector import FailureDetector
from .escalation import EscalationInterface
from .history import RecoveryHistory
from .models import FailureCategory, FailureReport, RecoveryAction, RecoveryRecord
from .replanning import ReplanningEngine
from .retry import RetryEngine, RetryPolicy
from .rollback import RollbackEngine


class RecoveryEngine:
    """Central orchestrator for agent failure detection, classification, retry, repair, replanning, rollback, and human escalation."""

    def __init__(
        self,
        retry_policy: RetryPolicy | None = None,
        max_failures_per_step: int = 3,
    ):
        self.detector = FailureDetector()
        self.classifier = FailureClassifier()
        self.retry_engine = RetryEngine(policy=retry_policy)
        self.alternative_engine = AlternativeToolEngine()
        self.replanning_engine = ReplanningEngine()
        self.rollback_engine = RollbackEngine()
        self.circuit_breaker = CircuitBreaker(max_failures_per_step=max_failures_per_step)
        self.history = RecoveryHistory()
        self.escalation = EscalationInterface()

    def handle_failure(
        self,
        task_id: str,
        step: TaskStep,
        execution_result: ActionResult | None,
        actual_state: dict[str, Any] | None,
        verified: bool,
        executor: ToolExecutor,
        observer: BaseObserver,
        verifier: BaseVerifier,
        planner: Planner | None = None,
    ) -> tuple[bool, ActionResult | None, dict[str, Any] | None, TaskPlan | None, str | None]:
        # 1. Detect Failure
        report = self.detector.detect(
            task_id=task_id,
            step=step,
            execution_result=execution_result,
            actual_state=actual_state,
            verified=verified,
        )
        if not report:
            return True, execution_result, actual_state, None, None

        # 2. Classify Failure
        report.category = self.classifier.classify(report)
        self.history.log_failure(report)

        # 3. Check Circuit Breaker
        cb_status = self.circuit_breaker.record_attempt(step.id)
        if cb_status.is_tripped:
            rec = RecoveryRecord(
                task_id=task_id,
                step_id=step.id,
                failure_report=report,
                action_taken=RecoveryAction.HUMAN_ESCALATION,
                attempt_number=cb_status.failure_count,
                success=False,
                details={"circuit_breaker": True, "reason": cb_status.reason},
            )
            self.history.log_recovery(rec)
            return False, execution_result, actual_state, None, cb_status.reason

        # 4. Strategy Selection A: Retry for transient/tool failures
        if self.retry_engine.is_retryable(report.category, cb_status.failure_count):
            retry_ok, retry_res, retry_state = self.retry_engine.execute_retry(
                step=step,
                executor=executor,
                observer=observer,
                verifier=verifier,
                attempt_number=cb_status.failure_count,
            )
            rec = RecoveryRecord(
                task_id=task_id,
                step_id=step.id,
                failure_report=report,
                action_taken=RecoveryAction.RETRY,
                attempt_number=cb_status.failure_count,
                success=retry_ok,
            )
            self.history.log_recovery(rec)

            if retry_ok:
                return True, retry_res, retry_state, None, None

        # 5. Strategy Selection B: Alternative Tool Substitution
        alt_ok, alt_tool, alt_res, alt_state = self.alternative_engine.execute_alternative(
            step=step,
            executor=executor,
            observer=observer,
            verifier=verifier,
        )
        if alt_tool:
            rec = RecoveryRecord(
                task_id=task_id,
                step_id=step.id,
                failure_report=report,
                action_taken=RecoveryAction.ALTERNATIVE_TOOL,
                attempt_number=cb_status.failure_count,
                success=alt_ok,
                details={"alternative_tool": alt_tool},
            )
            self.history.log_recovery(rec)

            if alt_ok:
                step.tool_name = alt_tool  # Update step tool reference
                return True, alt_res, alt_state, None, None

        # 6. Strategy Selection C: Replanning Engine
        replanned_plan = self.replanning_engine.replan_failed_step(step, report)
        if replanned_plan:
            rec = RecoveryRecord(
                task_id=task_id,
                step_id=step.id,
                failure_report=report,
                action_taken=RecoveryAction.REPLAN,
                attempt_number=cb_status.failure_count,
                success=True,
                details={"new_steps_count": len(replanned_plan.steps)},
            )
            self.history.log_recovery(rec)
            return False, execution_result, actual_state, replanned_plan, None

        # 7. Escalation Fallback
        esc_info = self.escalation.escalate(report)
        return False, execution_result, actual_state, None, esc_info["reason"]
