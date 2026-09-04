from typing import Any
from .approval import HumanApprovalManager
from .audit import SecurityAuditLogger
from .classifier import ActionClassifier
from .models import PermissionState, RiskLevel, SecurityDecision
from .permissions import PermissionManager
from .policy import PolicyEngine
from .risk import RiskAnalyzer
from .sandbox import RestrictedSandbox
from .secrets import SecretDetector


class SecurityManager:
    """Central Security Gate orchestrator serving as the mandatory authorization gate before tool/skill execution."""

    def __init__(
        self,
        risk_analyzer: RiskAnalyzer | None = None,
        policy_engine: PolicyEngine | None = None,
        permission_manager: PermissionManager | None = None,
        approval_manager: HumanApprovalManager | None = None,
        sandbox: RestrictedSandbox | None = None,
        audit_logger: SecurityAuditLogger | None = None,
    ):
        self.risk_analyzer = risk_analyzer or RiskAnalyzer()
        self.classifier = ActionClassifier(risk_analyzer=self.risk_analyzer)
        self.policy_engine = policy_engine or PolicyEngine()
        self.permission_manager = permission_manager or PermissionManager()
        self.approval_manager = approval_manager or HumanApprovalManager()
        self.sandbox = sandbox or RestrictedSandbox()
        self.secret_detector = SecretDetector()
        self.audit_logger = audit_logger or SecurityAuditLogger(secret_detector=self.secret_detector)

    def authorize(self, tool_name: str, arguments: dict[str, Any]) -> SecurityDecision:
        """Main security gate authorization method (Fails Closed on error)."""
        try:
            # 1. Action Extraction & Classification
            norm_action, risk = self.classifier.classify(tool_name, arguments)

            # 2. Secret / Sensitive Credential check
            if norm_action.data_sensitivity == "SENSITIVE" or self.secret_detector.contains_secret(norm_action.target):
                decision = SecurityDecision(
                    action=tool_name,
                    target=norm_action.target,
                    risk_level=RiskLevel.CRITICAL,
                    permission=PermissionState.DENY,
                    policy_result="DENY",
                    approval_required=False,
                    approval_status="DENIED",
                    reason="Access or modification of credentials/secrets is strictly blocked by security rule.",
                    allowed=False,
                )
                self.audit_logger.log_decision(decision)
                return decision

            # 3. Sandbox path validation
            path_ok, path_msg = self.sandbox.validate_path(norm_action.target)
            if not path_ok:
                decision = SecurityDecision(
                    action=tool_name,
                    target=norm_action.target,
                    risk_level=RiskLevel.HIGH,
                    permission=PermissionState.DENY,
                    policy_result="DENY",
                    approval_required=False,
                    approval_status="DENIED",
                    reason=path_msg,
                    allowed=False,
                )
                self.audit_logger.log_decision(decision)
                return decision

            # 4. Capability Permission Check
            perm_name = self.permission_manager.get_permission_for_tool(tool_name)
            perm_state = self.permission_manager.check(perm_name)
            if perm_state == PermissionState.DENY:
                decision = SecurityDecision(
                    action=tool_name,
                    target=norm_action.target,
                    risk_level=risk,
                    permission=PermissionState.DENY,
                    policy_result="DENY",
                    allowed=False,
                    reason=f"Capability permission '{perm_name}' is explicitly DENIED.",
                )
                self.audit_logger.log_decision(decision)
                return decision

            # 5. Policy Engine Evaluation
            pol_state, pol_reason = self.policy_engine.evaluate(norm_action)
            if pol_state == PermissionState.DENY:
                decision = SecurityDecision(
                    action=tool_name,
                    target=norm_action.target,
                    risk_level=risk,
                    permission=PermissionState.DENY,
                    policy_result="DENY",
                    allowed=False,
                    reason=pol_reason,
                )
                self.audit_logger.log_decision(decision)
                return decision

            # 6. Human Approval System Evaluation
            if pol_state == PermissionState.APPROVAL_REQUIRED or perm_state == PermissionState.APPROVAL_REQUIRED or risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                appr_ok, appr_msg = self.approval_manager.evaluate_request(norm_action, pol_reason)
                decision = SecurityDecision(
                    action=tool_name,
                    target=norm_action.target,
                    risk_level=risk,
                    permission=PermissionState.APPROVAL_REQUIRED,
                    policy_result="APPROVAL_REQUIRED",
                    approval_required=True,
                    approval_status="APPROVED" if appr_ok else "DENIED",
                    reason=appr_msg,
                    allowed=appr_ok,
                )
                self.audit_logger.log_decision(decision)
                return decision

            # 7. Auto-Allow
            decision = SecurityDecision(
                action=tool_name,
                target=norm_action.target,
                risk_level=risk,
                permission=PermissionState.ALLOW,
                policy_result="ALLOW",
                approval_required=False,
                approval_status="NOT_REQUIRED",
                reason=pol_reason,
                allowed=True,
            )
            self.audit_logger.log_decision(decision)
            return decision

        except Exception as exc:
            # Rule 9: Fail Closed -- Any unexpected security infrastructure failure blocks execution
            fail_closed_decision = SecurityDecision(
                action=tool_name,
                target=str(arguments.get("path", "")),
                risk_level=RiskLevel.CRITICAL,
                permission=PermissionState.DENY,
                policy_result="DENY",
                allowed=False,
                reason=f"Security gate error (Fails Closed): {exc}",
            )
            self.audit_logger.log_decision(fail_closed_decision)
            return fail_closed_decision
