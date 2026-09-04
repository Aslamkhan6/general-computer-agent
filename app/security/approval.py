from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
import uuid
from .models import NormalizedAction, RiskLevel


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: f"appr-{uuid.uuid4().hex[:8]}")
    action: str
    target: str
    risk_level: RiskLevel
    reason: str
    reversible: bool = True
    tool: str = ""
    status: str = "PENDING"  # PENDING, APPROVED, DENIED, TIMEOUT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: float = 30.0


class HumanApprovalManager:
    """Manages human approval requests, responses, pending approvals, and approval timeouts."""

    def __init__(self, default_auto_approve_test: bool = False):
        self._pending: dict[str, ApprovalRequest] = {}
        self.default_auto_approve_test = default_auto_approve_test

    def create_request(self, norm_action: NormalizedAction, reason: str) -> ApprovalRequest:
        req = ApprovalRequest(
            action=norm_action.tool,
            target=norm_action.target,
            risk_level=norm_action.potential_impact,
            reason=reason,
            reversible=norm_action.reversible,
            tool=norm_action.tool,
        )
        self._pending[req.id] = req
        return req

    def respond(self, request_id: str, approved: bool = True) -> ApprovalRequest | None:
        if request_id in self._pending:
            req = self._pending[request_id]
            req.status = "APPROVED" if approved else "DENIED"
            del self._pending[request_id]
            return req
        return None

    def evaluate_request(self, norm_action: NormalizedAction, reason: str) -> tuple[bool, str]:
        req = self.create_request(norm_action, reason)
        if self.default_auto_approve_test:
            req.status = "APPROVED"
            del self._pending[req.id]
            return True, f"Approved by user request [{req.id}]"

        # Simulating non-blocking prompt: if auto_approve is False, default to requiring response or timing out -> DENY
        # Default safety rule: Approval timeout or unhandled request = BLOCK (DENIED)
        req.status = "DENIED"
        if req.id in self._pending:
            del self._pending[req.id]
        return False, f"Human approval requested for [{req.action}] on [{req.target}] (Risk: {req.risk_level.value}) but timed out/denied by safety policy."

    def list_pending(self) -> list[dict[str, Any]]:
        return [r.model_dump() for r in self._pending.values()]
