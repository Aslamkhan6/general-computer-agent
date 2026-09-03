from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    PERMISSION = "PERMISSION"
    VALIDATION = "VALIDATION"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    ENVIRONMENT = "ENVIRONMENT"
    TOOL = "TOOL"
    VERIFICATION = "VERIFICATION"
    UNKNOWN = "UNKNOWN"


class RecoveryAction(str, Enum):
    RETRY = "RETRY"
    REPAIR = "REPAIR"
    ALTERNATIVE_TOOL = "ALTERNATIVE_TOOL"
    REPLAN = "REPLAN"
    ROLLBACK = "ROLLBACK"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"


class FailureReport(BaseModel):
    id: str = Field(default_factory=lambda: f"fail-{uuid.uuid4().hex[:8]}")
    task_id: str
    step_id: str
    error_message: str
    category: FailureCategory = FailureCategory.UNKNOWN
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecoveryRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:8]}")
    task_id: str
    step_id: str
    failure_report: FailureReport
    action_taken: RecoveryAction
    attempt_number: int = 1
    success: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, Any] = Field(default_factory=dict)
