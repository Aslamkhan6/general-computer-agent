from typing import Any
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.supervisor.supervisor import Supervisor
from .base import BaseTool

_supervisor_instance = Supervisor()


class ListAgentsTool(BaseTool):
    name = "list_agents"
    description = "List all registered worker agents and their roles/capabilities."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            agents = _supervisor_instance.registry.list_agents()
            return ActionResult(status=ActionStatus.SUCCESS, output={"agents_count": len(agents), "agents": agents})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetAgentStatusTool(BaseTool):
    name = "get_agent_status"
    description = "Query status, heartbeat, and metrics for a specific worker agent."
    risk_level = RiskLevel.LOW
    parameters = {"agent_id": "string"}

    def execute(self, agent_id: str) -> ActionResult:
        try:
            agent = _supervisor_instance.registry.get(agent_id)
            return ActionResult(status=ActionStatus.SUCCESS, output=agent.model_dump())
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetTaskStatusTool(BaseTool):
    name = "get_task_status"
    description = "Query current Supervisor state and task context."
    risk_level = RiskLevel.LOW
    parameters = {"task_id": "string"}

    def execute(self, task_id: str) -> ActionResult:
        try:
            ctx = _supervisor_instance.context_manager.get_context(task_id)
            return ActionResult(status=ActionStatus.SUCCESS, output={"supervisor_state": _supervisor_instance.state.value, "task_context": ctx})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class DispatchTaskTool(BaseTool):
    name = "dispatch_task"
    description = "Dispatch a subtask to a specialized worker agent."
    risk_level = RiskLevel.MEDIUM
    parameters = {"description": "string", "assigned_role": "string", "parent_task_id": "string (optional)"}

    def execute(self, description: str, assigned_role: str = "CODING", parent_task_id: str = "task-sup-001") -> ActionResult:
        try:
            from app.supervisor.models import AgentRole, SubTask
            role_enum = AgentRole(assigned_role) if hasattr(AgentRole, assigned_role) else AgentRole.CODING
            sub = SubTask(parent_task_id=parent_task_id, description=description, assigned_role=role_enum)
            worker = _supervisor_instance.dispatcher.dispatch(sub)
            return ActionResult(status=ActionStatus.SUCCESS, output={"subtask_id": sub.id, "assigned_worker": worker.name, "worker_role": worker.role.value})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetActiveTasksTool(BaseTool):
    name = "get_active_tasks"
    description = "List all active subtasks under supervision."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            health_info = _supervisor_instance.health_monitor.check_health()
            return ActionResult(status=ActionStatus.SUCCESS, output={"supervisor_state": _supervisor_instance.state.value, "health": health_info})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetAgentResultsTool(BaseTool):
    name = "get_agent_results"
    description = "Retrieve aggregated results returned by worker agents."
    risk_level = RiskLevel.LOW
    parameters = {"task_id": "string"}

    def execute(self, task_id: str) -> ActionResult:
        try:
            results = _supervisor_instance.result_manager.get_results_for_task(task_id)
            return ActionResult(status=ActionStatus.SUCCESS, output={"task_id": task_id, "results": [r.model_dump() for r in results]})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
