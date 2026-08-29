from datetime import datetime,timezone
from typing import Any
from pydantic import BaseModel, Field

from .enums  import (
    ActionStatus,
    RiskLevel,
    StepStatus,
    TaskStatus

)


class TaskStep(BaseModel):
    id: str

    description: str

    status: StepStatus = StepStatus.PENDING

    tool_name: str | None = None

    input_data: dict[str, Any] = Field(
        default_factory=dict
    )

    expected_state: dict[str, Any] = Field(
        default_factory=dict
    )

    output_data: dict[str, Any] = Field(
        default_factory=dict
    )

    depends_on: list[str] = Field(
        default_factory=list
    )

    error: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime | None = None


class ActionResult(BaseModel):
    status: ActionStatus

    output: Any = None
    error: str | None = None

    execution_time: float | None = None


class AgentTask(BaseModel):
    id: str

    user_request: str

    status: TaskStatus = TaskStatus.CREATED

    risk_level: RiskLevel = RiskLevel.LOW

    steps: list[TaskStep] = Field(default_factory=list)

    current_step_id: str | None = None

    context: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    final_result: Any = None

    error: str | None = None

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)