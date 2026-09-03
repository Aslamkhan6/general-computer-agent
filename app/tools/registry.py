from typing import Any

from .base import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level.value if hasattr(tool.risk_level, "value") else str(tool.risk_level),
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]


def register_all_default_tools(registry: ToolRegistry) -> None:
    from .filesystem import (
        ReadFileTool, WriteFileTool, CreateFileTool, CreateDirectoryTool,
        DeleteFileTool, DeleteDirectoryTool, CopyTool, MoveTool, RenameTool,
        ListDirectoryTool, SearchFilesTool, GetMetadataTool
    )
    from .terminal import (
        ExecuteCommandTool, RunPowerShellTool, StartProcessTool, StopProcessTool,
        GetProcessTool, InstallPackageTool
    )
    from .git import (
        GitInitTool, GitStatusTool, GitAddTool, GitCommitTool, GitBranchTool,
        GitCheckoutTool, GitPullTool, GitPushTool, GitCloneTool, GitDiffTool, GitLogTool
    )
    from .browser import (
        OpenUrlTool, BrowserSearchTool, BrowserNavigateTool, ExtractTextTool,
        ScreenshotTool, DownloadFileTool
    )
    from .application import (
        OpenApplicationTool, CloseApplicationTool, FocusApplicationTool,
        ListWindowsTool, GetActiveWindowTool
    )
    from .gui import (
        ScreenCaptureTool, MouseClickTool, MouseMoveTool, KeyboardTypeTool,
        KeyboardHotkeyTool, WindowActionTool, AccessibilityInspectTool,
        VisualGroundingClickTool
    )
    from .voice import (
        VoiceListenTool, VoiceTranscribeTool, VoiceSpeakTool, VoiceStopSpeakingTool,
        VoiceGetStateTool
    )
    from .memory_tools import (
        RememberPreferenceTool, RetrieveMemoriesTool, ListSkillsTool, ExecuteSkillTool,
        GetSessionContextTool
    )
    from .recovery_tools import (
        GetRecoveryHistoryTool, GetCircuitBreakerStatusTool, TriggerRollbackTool
    )

    tools = [
        # Filesystem
        ReadFileTool(), WriteFileTool(), CreateFileTool(), CreateDirectoryTool(),
        DeleteFileTool(), DeleteDirectoryTool(), CopyTool(), MoveTool(), RenameTool(),
        ListDirectoryTool(), SearchFilesTool(), GetMetadataTool(),
        # Terminal
        ExecuteCommandTool(), RunPowerShellTool(), StartProcessTool(), StopProcessTool(),
        GetProcessTool(), InstallPackageTool(),
        # Git
        GitInitTool(), GitStatusTool(), GitAddTool(), GitCommitTool(), GitBranchTool(),
        GitCheckoutTool(), GitPullTool(), GitPushTool(), GitCloneTool(), GitDiffTool(), GitLogTool(),
        # Browser
        OpenUrlTool(), BrowserSearchTool(), BrowserNavigateTool(), ExtractTextTool(),
        ScreenshotTool(), DownloadFileTool(),
        # Application
        OpenApplicationTool(), CloseApplicationTool(), FocusApplicationTool(),
        ListWindowsTool(), GetActiveWindowTool(),
        # GUI & Vision
        ScreenCaptureTool(), MouseClickTool(), MouseMoveTool(), KeyboardTypeTool(),
        KeyboardHotkeyTool(), WindowActionTool(), AccessibilityInspectTool(),
        VisualGroundingClickTool(),
        # Voice Intelligence
        VoiceListenTool(), VoiceTranscribeTool(), VoiceSpeakTool(), VoiceStopSpeakingTool(),
        VoiceGetStateTool(),
        # Memory & Skills
        RememberPreferenceTool(), RetrieveMemoriesTool(), ListSkillsTool(), ExecuteSkillTool(),
        GetSessionContextTool(),
        # Recovery & Reliability
        GetRecoveryHistoryTool(), GetCircuitBreakerStatusTool(), TriggerRollbackTool(),
    ]

    for tool in tools:
        if tool.name not in registry._tools:
            registry.register(tool)