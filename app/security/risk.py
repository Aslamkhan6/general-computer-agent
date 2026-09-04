from pathlib import Path
from .models import NormalizedAction, OperationType, RiskLevel


class RiskAnalyzer:
    """Analyzes actions across multiple dimensions (operation, target, reversibility, sensitivity, impact) to determine risk level."""

    CRITICAL_TARGET_PATTERNS = [
        r"c:\\windows",
        r"system32",
        r"/etc/",
        r"/boot/",
        r"\.env",
        r"id_rsa",
        r"credentials",
        r"passwords",
        r"shadow",
    ]

    SENSITIVE_DATA_KEYWORDS = [
        "password",
        "api_key",
        "secret",
        "token",
        "private_key",
        "credential",
    ]

    def analyze(self, action: NormalizedAction) -> RiskLevel:
        target_lower = action.target.lower()

        # 1. Critical target check
        for pat in self.CRITICAL_TARGET_PATTERNS:
            if pat in target_lower:
                return RiskLevel.CRITICAL

        # 2. Secret / credential sensitivity check
        for kw in self.SENSITIVE_DATA_KEYWORDS:
            if kw in target_lower or kw in action.data_sensitivity.lower():
                return RiskLevel.CRITICAL

        # 3. Operation-based risk evaluation
        if action.operation == OperationType.DELETE:
            if not action.reversible or "project" in target_lower or "folder" in target_lower:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        elif action.operation in (OperationType.EXECUTE, OperationType.SYSTEM_CHANGE, OperationType.SEND):
            return RiskLevel.HIGH
        elif action.operation in (OperationType.CREATE, OperationType.WRITE, OperationType.MODIFY, OperationType.INSTALL):
            return RiskLevel.MEDIUM
        elif action.operation in (OperationType.READ, OperationType.DOWNLOAD):
            return RiskLevel.LOW

        return RiskLevel.LOW
