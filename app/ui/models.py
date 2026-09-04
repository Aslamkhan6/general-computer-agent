"""
UI State Models and Enums for Nexus Agent Command Center.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RobotState(str, Enum):
    """Robot Brain visualization states."""
    STANDBY = "STANDBY"
    ANALYZING = "ANALYZING"
    WORKING = "WORKING"
    VERIFYING = "VERIFYING"
    RECOVERY = "RECOVERY"
    APPROVAL = "APPROVAL"
    COMPLETE = "COMPLETE"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class AutonomyLevel(str, Enum):
    """Autonomy level controlling human oversight."""
    AUTONOMOUS = "AUTONOMOUS"  # Fully autonomous within safety bounds
    ASSISTED = "ASSISTED"      # Requires approval for medium/high risk actions
    MANUAL = "MANUAL"          # Requires step-by-step human confirmation


class NavigationTab(str, Enum):
    """Main navigation tabs in Nexus Command Center UI."""
    CONSOLE = "CONSOLE"
    TASKS = "TASKS"
    AGENTS = "AGENTS"
    COMPUTER = "COMPUTER"
    MEMORY = "MEMORY"
    SECURITY = "SECURITY"
    RECOVERY = "RECOVERY"
    SYSTEM = "SYSTEM"


class SystemMetrics(BaseModel):
    """Diagnostic metrics for host system."""
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    disk_percent: float = 0.0
    network_kbps: float = 0.0
    uptime_seconds: float = 0.0


class UIState(BaseModel):
    """Overall state model for the Nexus Agent UI."""
    robot_state: RobotState = RobotState.STANDBY
    autonomy_level: AutonomyLevel = AutonomyLevel.ASSISTED
    active_tab: NavigationTab = NavigationTab.CONSOLE
    metrics: SystemMetrics = Field(default_factory=SystemMetrics)
    
    # Task Status
    active_task_id: Optional[str] = None
    active_task_goal: str = "System Idle"
    task_progress: float = 0.0  # 0.0 to 100.0
    active_tool_name: Optional[str] = None
    active_agent_role: Optional[str] = None
    
    # Flags & Counts
    is_voice_active: bool = False
    is_emergency_stopped: bool = False
    pending_approvals_count: int = 0
    recent_recovery_count: int = 0
    active_worker_count: int = 0
    
    # Recent log / status message
    status_message: str = "Nexus Command Center Initialized."

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary (Pydantic V2 compatible)."""
        return self.model_dump()
