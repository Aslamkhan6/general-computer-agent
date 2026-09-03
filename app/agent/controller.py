from datetime import datetime, timezone
from typing import Any

from app.core.enums import ActionStatus, StepStatus, TaskStatus
from app.core.events import Event, EventBus, EventType
from app.core.state import AgentTask, TaskStep
from app.observer.base import BaseObserver
from app.planner.plan import TaskPlan
from app.recovery.manager import RecoveryEngine
from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest
from app.verifier.base import BaseVerifier


class AgentController:

    def __init__(
        self,
        executor: ToolExecutor,
        observer: BaseObserver,
        verifier: BaseVerifier,
        event_bus: EventBus | None = None,
        recovery_engine: RecoveryEngine | None = None,
    ):
        self.executor = executor
        self.observer = observer
        self.verifier = verifier
        self.event_bus = event_bus
        self.recovery_engine = recovery_engine or RecoveryEngine()

    def _emit(
        self,
        event_type: EventType,
        task_id: str,
        step_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if self.event_bus:
            self.event_bus.publish(
                Event(
                    event_type=event_type,
                    task_id=task_id,
                    step_id=step_id,
                    payload=payload or {},
                )
            )

    def run_plan(self, task: AgentTask, plan: TaskPlan) -> AgentTask:
        """Execute a full task plan step-by-step with observation, verification & recovery."""
        task.status = TaskStatus.EXECUTING
        task.steps = plan.steps
        task.touch()
        self._emit(EventType.TASK_STARTED, task.id, payload={"goal": plan.goal, "total_steps": len(plan.steps)})

        step_idx = 0
        while step_idx < len(task.steps):
            step = task.steps[step_idx]
            task.current_step_id = step.id
            step.status = StepStatus.RUNNING
            task.touch()
            self._emit(EventType.STEP_STARTED, task.id, step.id, payload={"description": step.description})

            if not step.tool_name:
                step.status = StepStatus.FAILED
                step.error = "No tool specified for task step."
                task.status = TaskStatus.FAILED
                task.error = step.error
                task.touch()
                self._emit(EventType.STEP_FAILED, task.id, step.id, payload={"error": step.error})
                self._emit(EventType.TASK_FAILED, task.id, payload={"error": task.error})
                return task

            # 1. Execute
            request = ToolRequest(
                tool_name=step.tool_name,
                arguments=step.input_data,
            )
            execution_result = self.executor.execute(request)
            self._emit(
                EventType.STEP_EXECUTED,
                task.id,
                step.id,
                payload={"status": execution_result.status, "output": execution_result.output, "error": execution_result.error},
            )

            # 2. Observe & Verify
            observation_path = step.input_data.get("path", "")
            actual_state = self.observer.observe(path=observation_path)
            step.output_data = actual_state
            self._emit(EventType.STEP_OBSERVED, task.id, step.id, payload={"observed_state": actual_state})

            verified = False
            if execution_result.status == ActionStatus.SUCCESS:
                task.status = TaskStatus.VERIFYING
                task.touch()
                verified = self.verifier.verify(expected=step.expected_state, actual=actual_state)
                self._emit(EventType.STEP_VERIFIED, task.id, step.id, payload={"verified": verified})

            # Check if step succeeded
            if execution_result.status == ActionStatus.SUCCESS and verified:
                step.status = StepStatus.SUCCESS
                step.completed_at = datetime.now(timezone.utc)
                self._emit(EventType.STEP_COMPLETED, task.id, step.id)
                step_idx += 1
                continue

            # 3. Engage Module 7 Recovery Engine upon failure
            recovered, rec_res, rec_state, replanned_plan, esc_reason = self.recovery_engine.handle_failure(
                task_id=task.id,
                step=step,
                execution_result=execution_result,
                actual_state=actual_state,
                verified=verified,
                executor=self.executor,
                observer=self.observer,
                verifier=self.verifier,
            )

            if recovered:
                step.status = StepStatus.SUCCESS
                step.completed_at = datetime.now(timezone.utc)
                self._emit(EventType.STEP_COMPLETED, task.id, step.id)
                step_idx += 1
            elif replanned_plan:
                # Insert replanned recovery steps
                task.steps[step_idx:step_idx+1] = replanned_plan.steps
                # Loop continues with first inserted step
            else:
                # Failure unrecoverable
                step.status = StepStatus.FAILED
                step.error = esc_reason or execution_result.error or "Step failed and recovery was unrecoverable."
                task.status = TaskStatus.FAILED
                task.error = step.error
                task.touch()
                self._emit(EventType.STEP_FAILED, task.id, step.id, payload={"error": step.error})
                self._emit(EventType.TASK_FAILED, task.id, payload={"error": task.error})
                return task

        task.status = TaskStatus.COMPLETED
        task.final_result = {
            "verified": True,
            "steps_completed": len(task.steps),
        }
        task.touch()
        self._emit(EventType.TASK_COMPLETED, task.id, payload={"final_result": task.final_result})

        return task

    def execute_task(
        self,
        task: AgentTask,
        request: ToolRequest,
        expected_state: dict[str, Any],
        observation_path: str,
    ) -> AgentTask:
        """Legacy single-request execution interface."""
        step = TaskStep(
            id="step-001",
            description=f"Execute {request.tool_name}",
            status=StepStatus.PENDING,
            tool_name=request.tool_name,
            input_data=request.arguments,
            expected_state=expected_state,
        )
        plan = TaskPlan(
            goal=task.user_request,
            steps=[step],
        )
        return self.run_plan(task, plan)