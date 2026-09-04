from typing import Any
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.security.manager import SecurityManager
from .base import BaseTool

_security_manager = SecurityManager()


class GetSecurityStatusTool(BaseTool):
    name = "get_security_status"
    description = "Get current Module 8 security manager status and policies."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={
                    "security_active": True,
                    "permissions_count": len(_security_manager.permission_manager.list_permissions()),
                    "pending_approvals_count": len(_security_manager.approval_manager.list_pending()),
                    "audit_logs_count": len(_security_manager.audit_logger.get_logs()),
                },
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class RequestApprovalTool(BaseTool):
    name = "request_approval"
    description = "Submit a request for human approval on a high-risk action."
    risk_level = RiskLevel.MEDIUM
    parameters = {"action": "string", "target": "string", "reason": "string"}

    def execute(self, action: str, target: str, reason: str = "User approval required") -> ActionResult:
        try:
            norm_action = _security_manager.classifier.normalize(action, {"path": target})
            appr_req = _security_manager.approval_manager.create_request(norm_action, reason)
            return ActionResult(status=ActionStatus.SUCCESS, output=appr_req.model_dump())
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetPendingApprovalsTool(BaseTool):
    name = "get_pending_approvals"
    description = "List all pending human approval requests."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            pending = _security_manager.approval_manager.list_pending()
            return ActionResult(status=ActionStatus.SUCCESS, output={"pending_approvals": pending})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetAuditLogTool(BaseTool):
    name = "get_audit_log"
    description = "Retrieve sanitized security audit decision logs."
    risk_level = RiskLevel.LOW
    parameters = {"limit": "integer (optional, default 50)"}

    def execute(self, limit: int = 50) -> ActionResult:
        try:
            logs = _security_manager.audit_logger.get_logs(limit=limit)
            return ActionResult(status=ActionStatus.SUCCESS, output={"audit_logs": logs})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetPermissionsTool(BaseTool):
    name = "get_permissions"
    description = "List all capability permissions and their current authorization states."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            perms = _security_manager.permission_manager.list_permissions()
            return ActionResult(status=ActionStatus.SUCCESS, output={"permissions": perms})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
