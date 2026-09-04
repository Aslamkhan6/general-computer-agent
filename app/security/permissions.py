from typing import Any
from .models import PermissionState


class PermissionManager:
    """Manages capability-based permissions for the computer agent."""

    DEFAULT_PERMISSIONS = {
        "filesystem.read": PermissionState.ALLOW,
        "filesystem.write": PermissionState.ALLOW,
        "filesystem.delete": PermissionState.APPROVAL_REQUIRED,
        "terminal.execute": PermissionState.ALLOW,
        "browser.control": PermissionState.ALLOW,
        "network.access": PermissionState.ALLOW,
        "microphone.access": PermissionState.ALLOW,
        "screen.capture": PermissionState.ALLOW,
        "email.send": PermissionState.APPROVAL_REQUIRED,
        "credential.access": PermissionState.DENY,
    }

    def __init__(self, permissions: dict[str, PermissionState] | None = None):
        self._permissions = dict(self.DEFAULT_PERMISSIONS)
        if permissions:
            self._permissions.update(permissions)

    def get_permission_for_tool(self, tool_name: str) -> str:
        if "delete" in tool_name or "remove" in tool_name:
            return "filesystem.delete"
        elif "write" in tool_name or "create" in tool_name or "copy" in tool_name or "move" in tool_name:
            return "filesystem.write"
        elif "read" in tool_name or "list" in tool_name or "search" in tool_name:
            return "filesystem.read"
        elif "command" in tool_name or "powershell" in tool_name or "process" in tool_name:
            return "terminal.execute"
        elif "browser" in tool_name or "url" in tool_name:
            return "browser.control"
        elif "screen" in tool_name or "capture" in tool_name or "gui" in tool_name or "mouse" in tool_name or "keyboard" in tool_name:
            return "screen.capture"
        elif "voice" in tool_name or "listen" in tool_name:
            return "microphone.access"
        return "filesystem.read"

    def check(self, permission_name: str) -> PermissionState:
        return self._permissions.get(permission_name, PermissionState.APPROVAL_REQUIRED)

    def grant(self, permission_name: str, state: PermissionState = PermissionState.ALLOW) -> None:
        self._permissions[permission_name] = state

    def list_permissions(self) -> dict[str, str]:
        return {k: v.value for k, v in self._permissions.items()}
