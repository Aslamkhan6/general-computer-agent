from datetime import datetime, timezone
from typing import Any
from .models import AgentStatus, WorkerAgentInfo
from .registry import AgentRegistry


class HealthMonitor:
    """Monitors worker agent health, heartbeats, success/failure metrics, and responsiveness."""

    def __init__(self, registry: AgentRegistry | None = None, heartbeat_timeout_seconds: float = 300.0):
        self.registry = registry or AgentRegistry()
        self.timeout_seconds = heartbeat_timeout_seconds

    def heartbeat(self, agent_id: str) -> None:
        agent = self.registry.get(agent_id)
        agent.last_heartbeat = datetime.now(timezone.utc)
        if agent.status == AgentStatus.UNHEALTHY:
            agent.status = AgentStatus.IDLE

    def record_success(self, agent_id: str) -> None:
        agent = self.registry.get(agent_id)
        agent.success_count += 1
        agent.status = AgentStatus.IDLE
        agent.current_task_id = None
        self.heartbeat(agent_id)

    def record_failure(self, agent_id: str) -> None:
        agent = self.registry.get(agent_id)
        agent.failure_count += 1
        agent.status = AgentStatus.FAILED
        self.heartbeat(agent_id)

    def check_health(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        unhealthy = []
        for agent in self.registry._agents.values():
            if (now - agent.last_heartbeat).total_seconds() > self.timeout_seconds:
                agent.status = AgentStatus.UNHEALTHY
                unhealthy.append(agent.id)
        return {"unhealthy_agents_count": len(unhealthy), "unhealthy_agents": unhealthy}
