from datetime import datetime, timezone

from app.core.enums import StepStatus, TaskStatus
from app.core.state import AgentTask
from app.observer.filesystem import FilesystemObserver
from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest
from app.verifier.filesystem import FilesystemVerifier


class AgentController:

    def __init__(
        self,
        executor: ToolExecutor,
        observer: FilesystemObserver,
        verifier: FilesystemVerifier,
    ):
        self.executor = executor
        self.observer = observer
        self.verifier = verifier

    def execute_task(
        self,
        task: AgentTask,
        request: ToolRequest,
        expected_state: dict,
        observation_path: str,
    ) -> AgentTask:

        task.status = TaskStatus.EXECUTING
        task.updated_at = datetime.now(timezone.utc)

        # --------------------------------
        # Create task step
        # --------------------------------

        step = {
            "id": "step-001",
            "description": f"Execute {request.tool_name}",
            "status": StepStatus.RUNNING,
            "tool_name": request.tool_name,
            "input_data": request.arguments,
        }

        task.steps.append(step)

        task.current_step_id = "step-001"

        # --------------------------------
        # Execute
        # --------------------------------

        execution_result = self.executor.execute(request)

        if execution_result.status != "success":

            task.status = TaskStatus.FAILED
            task.error = execution_result.error

            step["status"] = StepStatus.FAILED
            step["error"] = execution_result.error

            return task

        # --------------------------------
        # Observe
        # --------------------------------

        actual_state = self.observer.observe(
            path=observation_path
        )

        step["output_data"] = actual_state

        # --------------------------------
        # Verify
        # --------------------------------

        task.status = TaskStatus.VERIFYING

        verified = self.verifier.verify(
            expected=expected_state,
            actual=actual_state,
        )

        if verified:

            step["status"] = StepStatus.SUCCESS

            step["completed_at"] = datetime.now(
                timezone.utc
            )

            task.status = TaskStatus.COMPLETED

            task.final_result = {
                "verified": True,
                "state": actual_state,
            }

        else:

            step["status"] = StepStatus.FAILED

            task.status = TaskStatus.FAILED

            task.error = (
                "Verification failed. "
                "Actual state did not match expected state."
            )

            task.final_result = {
                "verified": False,
                "state": actual_state,
            }

        task.updated_at = datetime.now(timezone.utc)

        return task