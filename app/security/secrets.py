import re
from typing import Any


class SecretDetector:
    """Detects credentials, API keys, tokens, and redacts them to prevent leakages in audit logs."""

    SECRET_PATTERNS = [
        (r"(?i)(api[_-]?key|secret|password|passwd|auth[_-]?token|bearer)\s*=\s*['\"]?([^'\"\s]+)['\"]?", r"\1=****************"),
        (r"sk-[a-zA-Z0-9]{20,}", "sk-****************"),
        (r"ghp_[a-zA-Z0-9]{20,}", "ghp_****************"),
        (r"AKIA[0-9A-Z]{16}", "AKIA****************"),
        (r"-----BEGIN PRIVATE KEY-----[\s\S]*?-----END PRIVATE KEY-----", "*****REDACTED PRIVATE KEY*****"),
    ]

    def contains_secret(self, text: str) -> bool:
        for pattern, _ in self.SECRET_PATTERNS:
            if re.search(pattern, text):
                return True
        return False

    def sanitize_text(self, text: str) -> str:
        sanitized = text
        for pattern, replacement in self.SECRET_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        clean = {}
        for k, v in data.items():
            if any(kw in k.lower() for kw in ["password", "secret", "token", "key", "auth", "credential"]):
                clean[k] = "****************"
            elif isinstance(v, str):
                clean[k] = self.sanitize_text(v)
            elif isinstance(v, dict):
                clean[k] = self.sanitize_dict(v)
            else:
                clean[k] = v
        return clean
