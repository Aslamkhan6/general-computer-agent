from typing import Any
from app.agent.controller import AgentController
from app.core.state import AgentTask
from .executor import SkillExecutor
from .models import Skill
from .registry import SkillRegistry


class SkillManager:
    """Unified Manager for Skill discovery, selection, and execution."""

    def __init__(self, registry: SkillRegistry | None = None, controller: AgentController | None = None):
        self.registry = registry or SkillRegistry()
        self.controller = controller
        self.executor = SkillExecutor(controller) if controller else None

    def list_available_skills(self) -> list[dict[str, Any]]:
        return self.registry.list_skills()

    def select_skill(self, goal: str) -> Skill | None:
        return self.registry.find_matching_skill(goal)

    def execute_skill_by_name(self, skill_name: str, inputs: dict[str, Any], task_id: str = "task-skill-001") -> AgentTask:
        if not self.executor:
            raise RuntimeError("AgentController is required on SkillManager to execute skills.")
        skill = self.registry.get(skill_name)
        return self.executor.execute_skill(skill, inputs, task_id=task_id)
