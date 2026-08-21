import re

from app.core.state import TaskStep
from .plan import TaskPlan


class Planner:

    def create_plan(self, goal: str) -> TaskPlan:

        match = re.search(
            r"(?:directory|folder)\s+(?:called|named)\s+['\"]?([^'\"]+)['\"]?",
            goal,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError(
                "Could not determine directory name."
            )

        directory_name = match.group(1).strip()

        path = f"./workspace/{directory_name}"

        step = TaskStep(
            id="step-001",
            description=(
                f"Create directory '{directory_name}'"
            ),
            tool_name="create_directory",
            input_data={
                "path": path
            },
            expected_state={
                "exists": True,
                "is_directory": True,
            },
        )

        return TaskPlan(
            goal=goal,
            steps=[step],
        )