from pathlib import Path
from typing import Any
from app.core.state import TaskStep
from app.planner.plan import TaskPlan
from .models import FailureCategory, FailureReport


class ReplanningEngine:
    """Generates revised task plans to recover from structural failures."""

    def replan_failed_step(self, step: TaskStep, report: FailureReport) -> TaskPlan | None:
        category = report.category

        # If parent directory not found, insert parent directory creation step
        if category == FailureCategory.NOT_FOUND or "parent" in report.error_message.lower():
            file_path = step.input_data.get("path")
            if file_path:
                parent_dir = str(Path(file_path).parent)
                step_parent = TaskStep(
                    id=f"{step.id}-replan-parent",
                    description=f"Create missing parent directory '{parent_dir}'",
                    tool_name="create_directory",
                    input_data={"path": parent_dir},
                    expected_state={"exists": True, "is_directory": True},
                )
                step_retry = TaskStep(
                    id=f"{step.id}-retry",
                    description=step.description,
                    tool_name=step.tool_name,
                    input_data=step.input_data,
                    expected_state=step.expected_state,
                )
                return TaskPlan(
                    goal=f"Replanned recovery for '{step.description}'",
                    steps=[step_parent, step_retry],
                )

        # Fallback default replan: wrap step with create_directory prerequisite
        file_path = step.input_data.get("path")
        if file_path:
            parent_dir = str(Path(file_path).parent)
            step_prereq = TaskStep(
                id=f"{step.id}-replan-prereq",
                description=f"Ensure workspace parent directory '{parent_dir}'",
                tool_name="create_directory",
                input_data={"path": parent_dir},
                expected_state={"exists": True, "is_directory": True},
            )
            return TaskPlan(
                goal=f"Replanned step recovery for step {step.id}",
                steps=[step_prereq, step],
            )

        return None
