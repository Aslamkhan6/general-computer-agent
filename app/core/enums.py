from enum import Enum
class TaskStatus(str,Enum):
    CREATED = "CREATED"
    PLANING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"

class StepStatus(str,Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class RiskLevel(str,Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionStatus(str,Enum):
    SUCCESS= "SUCCESS"
    FAILED ="FAILED"
    BLOCKED ="BLOCKED"
    REQUIRED_APPROVEL =  "REQUIRED_APPROVEL"
