"""
UI & Desktop Command Center Agent Tools for Module 10.
"""

from typing import Dict, Any, Optional
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.ui.models import RobotState
from .base import BaseTool


class GetUIStateTool(BaseTool):
    """Tool for retrieving current Nexus Command Center UI state."""

    name = "get_ui_state"
    description = "Retrieve current state of the Nexus Agent Command Center UI (robot state, autonomy level, progress)."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        return ActionResult(
            status=ActionStatus.SUCCESS,
            output={
                "robot_state": RobotState.STANDBY.value,
                "autonomy_level": "ASSISTED",
                "ui_active": True,
            }
        )


class SendUINotificationTool(BaseTool):
    """Tool for sending a log notification to the UI Command Center event stream."""

    name = "send_ui_notification"
    description = "Send a notification message to the Nexus Command Center visual event log stream."
    risk_level = RiskLevel.LOW
    parameters = {"message": "string", "level": "string (optional)"}

    def execute(self, message: str, level: str = "INFO") -> ActionResult:
        return ActionResult(
            status=ActionStatus.SUCCESS,
            output={"sent": True, "level": level, "message": message}
        )


class UpdateRobotStateTool(BaseTool):
    """Tool for updating the Robot Brain visual state in the UI."""

    name = "update_robot_state"
    description = "Update the Robot Brain visual state indicator (STANDBY, ANALYZING, WORKING, VERIFYING, RECOVERY, COMPLETE)."
    risk_level = RiskLevel.LOW
    parameters = {"state": "string", "active_tool": "string (optional)"}

    def execute(self, state: str, active_tool: str = "") -> ActionResult:
        return ActionResult(
            status=ActionStatus.SUCCESS,
            output={"robot_state": state.upper(), "active_tool": active_tool}
        )


class TriggerUIApprovalTool(BaseTool):
    """Tool for submitting a human authorization request to the UI Approval Center."""

    name = "trigger_ui_approval"
    description = "Submit a human approval request prompt to the UI Security Approval Center."
    risk_level = RiskLevel.MEDIUM
    parameters = {"request_id": "string", "action_summary": "string", "risk_level": "string (optional)"}

    def execute(self, request_id: str, action_summary: str, risk_level: str = "MEDIUM") -> ActionResult:
        return ActionResult(
            status=ActionStatus.SUCCESS,
            output={"request_id": request_id, "action_summary": action_summary, "risk_level": risk_level, "pending": True}
        )
