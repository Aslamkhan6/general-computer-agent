from typing import Any
from app.agent.controller import AgentController
from app.core.enums import TaskStatus
from app.core.state import AgentTask, TaskStep
from app.planner.plan import TaskPlan
from .models import Skill


class SkillExecutor:
    """Executes a skill workflow by expanding its steps and driving them through the AgentController."""

    def __init__(self, controller: AgentController):
        self.controller = controller

    def execute_skill(self, skill: Skill, inputs: dict[str, Any], task_id: str = "task-skill-001") -> AgentTask:
        # Validate inputs and format step templates
        steps: list[TaskStep] = []
        for s in skill.steps:
            formatted_input = {}
            for k, val_template in s.input_template.items():
                if isinstance(val_template, str):
                    formatted_val = val_template
                    for in_key, in_val in inputs.items():
                        formatted_val = formatted_val.replace(f"{{{in_key}}}", str(in_val))
                    formatted_input[k] = formatted_val
                else:
                    formatted_input[k] = val_template

            formatted_expected = {}
            for k, exp_template in s.expected_state.items():
                formatted_expected[k] = exp_template

            step = TaskStep(
                id=s.id,
                description=f"Skill '{skill.name}' step [{s.id}]: execute {s.tool_name}",
                tool_name=s.tool_name,
                input_data=formatted_input,
                expected_state=formatted_expected,
            )
            steps.append(step)

        plan = TaskPlan(
            goal=f"Execute Skill '{skill.name}'",
            steps=steps,
        )

        task = AgentTask(
            id=task_id,
            user_request=f"Skill: {skill.name}",
        )

        return self.controller.run_plan(task, plan)
