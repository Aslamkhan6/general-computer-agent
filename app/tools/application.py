import os
import subprocess
import sys
from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


class OpenApplicationTool(BaseTool):
    name = "open_application"
    description = "Launch a desktop application or executable by name or path."
    risk_level = RiskLevel.MEDIUM
    parameters = {"name_or_path": "string"}

    def execute(self, name_or_path: str) -> ActionResult:
        try:
            if sys.platform == "win32":
                proc = subprocess.Popen(f"start \"\" \"{name_or_path}\"", shell=True)
            else:
                proc = subprocess.Popen([name_or_path], shell=True)

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"application": name_or_path, "launched": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class CloseApplicationTool(BaseTool):
    name = "close_application"
    description = "Close an application process by process name."
    risk_level = RiskLevel.HIGH
    parameters = {"process_name": "string"}

    def execute(self, process_name: str) -> ActionResult:
        try:
            if sys.platform == "win32":
                cmd = f"taskkill /IM \"{process_name}\" /F"
            else:
                cmd = f"pkill -f \"{process_name}\""

            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return ActionResult(
                    status=ActionStatus.SUCCESS,
                    output={"process_name": process_name, "closed": True},
                )
            else:
                return ActionResult(status=ActionStatus.FAILED, error=res.stderr.strip())
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class FocusApplicationTool(BaseTool):
    name = "focus_application"
    description = "Bring an application window to focus."
    risk_level = RiskLevel.LOW
    parameters = {"title_or_name": "string"}

    def execute(self, title_or_name: str) -> ActionResult:
        try:
            if sys.platform == "win32":
                ps_script = f"""
                $app = Get-Process | Where-Object {{ $_.MainWindowTitle -like "*{title_or_name}*" -or $_.ProcessName -like "*{title_or_name}*" }} | Select-Object -First 1
                if ($app) {{
                    $wshell = New-Object -ComObject wscript.shell
                    $wshell.AppActivate($app.Id)
                }}
                """
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"target": title_or_name, "focused": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class ListWindowsTool(BaseTool):
    name = "list_windows"
    description = "List all active desktop application windows."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            windows = []
            if sys.platform == "win32":
                ps_cmd = "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json"
                res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
                stdout = res.stdout.strip()
                windows = [{"raw": stdout}]

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"windows": windows},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetActiveWindowTool(BaseTool):
    name = "get_active_window"
    description = "Get metadata of the currently active foreground window."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            active_window = {"title": "Active Window", "process": "explorer.exe"}
            if sys.platform == "win32":
                ps_cmd = """
                $code = @'
                [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
                [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
'@
                Add-Type -MemberDefinition $code -Name Win32Utils -Namespace Win32
                $hwnd = [Win32.Win32Utils]::GetForegroundWindow()
                $sb = New-Object System.Text.StringBuilder 256
                [void][Win32.Win32Utils]::GetWindowText($hwnd, $sb, 256)
                $sb.ToString()
                """
                res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
                title = res.stdout.strip()
                if title:
                    active_window["title"] = title

            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"active_window": active_window},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
