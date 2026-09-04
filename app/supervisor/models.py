from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class AgentRole(str, Enum):
    SUPERVISOR = "SUPERVISOR"
    RESEARCH = "RESEARCH"
    CODING = "CODING"
    COMPUTER = "COMPUTER"
    BROWSER = "BROWSER"
    VERIFICATION = "VERIFICATION"


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    OBSERVING = "OBSERVING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNHEALTHY = "UNHEALTHY"


class SupervisorState(str, Enum):
    IDLE = "IDLE"
    RECEIVING_TASK = "RECEIVING_TASK"
    ANALYZING = "ANALYZING"
    DECOMPOSING = "DECOMPOSING"
    DISPATCHING = "DISPATCHING"
    MONITORING = "MONITORING"
    AGGREGATING = "AGGREGATING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    RECOVERY = "RECOVERY"
    FAILED = "FAILED"


class WorkerAgentInfo(BaseModel):
    id: str = Field(default_factory=lambda: f"agent-{uuid.uuid4().hex[:8]}")
    name: str
    role: AgentRole
    capabilities: list[str] = Field(default_factory=list)
    supported_tasks: list[str] = Field(default_factory=list)
    required_permissions: list[str] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: str | None = None
    success_count: int = 0
    failure_count: int = 0
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: f"subtask-{uuid.uuid4().hex[:8]}")
    parent_task_id: str
    description: str
    assigned_role: AgentRole
    required_capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SharedTaskContext(BaseModel):
    task_id: str
    goal: str
    completed_subtasks: list[str] = Field(default_factory=list)
    subtask_outputs: dict[str, Any] = Field(default_factory=dict)
    shared_artifacts: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    task_id: str
    subtask_id: str
    agent_id: str
    status: AgentStatus
    output: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    execution_time_seconds: float = 0.0
    verified: bool = True
    errors: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    sender_id: str
    receiver_id: str
    task_id: str
    message_type: str = "RESULT"  # RESULT, STATUS_UPDATE, REQUEST_HELP, ARTIFACT
    content: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
