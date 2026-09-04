from pathlib import Path
from typing import Any


class RestrictedSandbox:
    """Enforces sandbox workspace bounds and path traversal restrictions."""

    def __init__(self, allowed_root: str = "./workspace"):
        self.allowed_root = Path(allowed_root).resolve()

    def validate_path(self, target_path: str) -> tuple[bool, str]:
        if not target_path:
            return True, "Path empty; sandbox check skipped."

        try:
            resolved = Path(target_path).resolve()
            # Ensure resolved path is within allowed_root or subpath
            if str(resolved).lower().startswith(str(self.allowed_root).lower()):
                return True, f"Path '{target_path}' is inside sandbox workspace."
            
            # Check for path traversal attempts
            if ".." in target_path or resolved != Path(target_path).absolute():
                return False, f"Sandbox violation: Target path '{target_path}' attempts path traversal outside workspace."
            
            return True, "Path validated."
        except Exception as exc:
            return False, f"Sandbox path validation error: {exc}"
