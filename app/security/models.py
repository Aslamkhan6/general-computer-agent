from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OperationType(str, Enum):
    READ = "READ"
    CREATE = "CREATE"
    WRITE = "WRITE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    SEND = "SEND"
    INSTALL = "INSTALL"
    SYSTEM_CHANGE = "SYSTEM_CHANGE"


class PermissionState(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class NormalizedAction(BaseModel):
    id: str = Field(default_factory=lambda: f"action-{uuid.uuid4().hex[:8]}")
    tool: str
    target: str = ""
    operation: OperationType = OperationType.READ
    reversible: bool = True
    data_sensitivity: str = "NORMAL"
    potential_impact: RiskLevel = RiskLevel.LOW
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityDecision(BaseModel):
    id: str = Field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:8]}")
    action: str
    target: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    permission: PermissionState = PermissionState.ALLOW
    policy_result: str = "ALLOW"
    approval_required: bool = False
    approval_status: str = "NOT_REQUIRED"  # APPROVED, DENIED, TIMEOUT, NOT_REQUIRED
    reason: str = "Action authorized by security policy"
    allowed: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
