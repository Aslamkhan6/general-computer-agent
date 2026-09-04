from typing import Any
from .models import SecurityDecision
from .secrets import SecretDetector


class SecurityAuditLogger:
    """Maintains an auditable, sanitized event log of all security authorization decisions."""

    def __init__(self, secret_detector: SecretDetector | None = None):
        self.secret_detector = secret_detector or SecretDetector()
        self._audit_records: list[dict[str, Any]] = []

    def log_decision(self, decision: SecurityDecision) -> None:
        rec = decision.model_dump()
        # Redact secrets from reason and target strings
        rec["reason"] = self.secret_detector.sanitize_text(rec["reason"])
        rec["target"] = self.secret_detector.sanitize_text(rec["target"])
        self._audit_records.append(rec)

    def get_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._audit_records[-limit:]

    def clear(self) -> None:
        self._audit_records.clear()
