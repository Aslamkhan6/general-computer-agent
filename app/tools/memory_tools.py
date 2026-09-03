from typing import Any
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.memory.manager import MemoryManager
from app.memory.models import MemorySource, MemoryType
from .base import BaseTool

_memory_manager = MemoryManager()


class RememberPreferenceTool(BaseTool):
    name = "remember_preference"
    description = "Store a user preference or fact in long-term memory."
    risk_level = RiskLevel.LOW
    parameters = {"content": "string", "memory_type": "string (optional, default USER_PREFERENCE)"}

    def execute(self, content: str, memory_type: str = "USER_PREFERENCE") -> ActionResult:
        try:
            m_type = MemoryType(memory_type) if hasattr(MemoryType, memory_type) else MemoryType.USER_PREFERENCE
            mem = _memory_manager.remember(content=content, memory_type=m_type, source=MemorySource.USER)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"memory_id": mem.id, "content": mem.content, "importance": mem.importance, "persistent": mem.persistent},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class RetrieveMemoriesTool(BaseTool):
    name = "retrieve_memories"
    description = "Retrieve top relevant memories for a user query."
    risk_level = RiskLevel.LOW
    parameters = {"query": "string", "top_k": "integer (optional, default 3)"}

    def execute(self, query: str, top_k: int = 3) -> ActionResult:
        try:
            ctx = _memory_manager.retrieve_relevant_context(query, top_k=top_k)
            return ActionResult(status=ActionStatus.SUCCESS, output=ctx)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class ListSkillsTool(BaseTool):
    name = "list_skills"
    description = "List available reusable high-level skills in the registry."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            skills = _memory_manager.skills.list_available_skills()
            return ActionResult(status=ActionStatus.SUCCESS, output={"skills": skills})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class ExecuteSkillTool(BaseTool):
    name = "execute_skill"
    description = "Execute a reusable skill workflow by name."
    risk_level = RiskLevel.HIGH
    parameters = {"skill_name": "string", "inputs": "dictionary of skill parameters"}

    def execute(self, skill_name: str, inputs: dict[str, Any]) -> ActionResult:
        try:
            if not _memory_manager.skills.controller:
                # Return skill plan template if controller is not bound directly on singleton
                skill = _memory_manager.skills.registry.get(skill_name)
                return ActionResult(status=ActionStatus.SUCCESS, output={"skill": skill.name, "inputs": inputs, "steps_count": len(skill.steps)})
            
            task = _memory_manager.skills.execute_skill_by_name(skill_name, inputs)
            return ActionResult(status=ActionStatus.SUCCESS, output={"task_id": task.id, "status": task.status.value, "final_result": task.final_result})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetSessionContextTool(BaseTool):
    name = "get_session_context"
    description = "Query current short-term session memory context."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            ctx = _memory_manager.short_term.get_context()
            return ActionResult(status=ActionStatus.SUCCESS, output={"context": ctx})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
