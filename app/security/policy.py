from .models import NormalizedAction, OperationType, PermissionState, RiskLevel


class PolicyEngine:
    """Evaluates security rules and policies for normalized actions."""

    def evaluate(self, action: NormalizedAction) -> tuple[PermissionState, str]:
        target = action.target.lower()

        # Rule: Critical target or credential read -> DENY
        if action.potential_impact == RiskLevel.CRITICAL:
            return PermissionState.DENY, "CRITICAL risk action target blocked by security policy."

        if any(kw in target for kw in ["\.env", "credentials", "passwords", "id_rsa", "shadow"]):
            return PermissionState.DENY, "Access to sensitive credentials/secrets is denied."

        # Rule: System file modification or deletion -> DENY
        if any(kw in target for kw in ["c:\\windows", "system32", "/etc/", "/boot/"]):
            return PermissionState.DENY, "Modification or deletion of operating system directories is denied."

        # Rule: Delete operation -> APPROVAL_REQUIRED
        if action.operation == OperationType.DELETE:
            return PermissionState.APPROVAL_REQUIRED, "File or directory deletion requires human authorization."

        # Rule: High risk operations -> APPROVAL_REQUIRED
        if action.potential_impact == RiskLevel.HIGH:
            return PermissionState.APPROVAL_REQUIRED, "HIGH risk operation requires human authorization."

        # Rule: Medium risk operations inside workspace -> ALLOW
        if action.potential_impact == RiskLevel.MEDIUM:
            return PermissionState.ALLOW, "MEDIUM risk workspace operation allowed by policy."

        # Rule: Low risk operations -> ALLOW
        if action.potential_impact == RiskLevel.LOW:
            return PermissionState.ALLOW, "LOW risk operation allowed by policy."

        # Rule 1: Default Deny for unknown actions
        return PermissionState.DENY, "Action denied by default security policy."
