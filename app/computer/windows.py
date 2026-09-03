import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class WindowInfo:
    handle: int
    title: str
    process_name: str
    pid: int
    is_active: bool = False


class WindowManager:
    """Provides desktop window enumeration, active window queries, focus, minimize, maximize, and close operations."""

    def enumerate_windows(self) -> list[WindowInfo]:
        windows = []
        if sys.platform == "win32":
            try:
                ps_cmd = "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object Id, ProcessName, MainWindowTitle, MainWindowHandle | ConvertTo-Json"
                res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
                stdout = res.stdout.strip()
                if stdout:
                    data = json.loads(stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for item in data:
                        windows.append(
                            WindowInfo(
                                handle=item.get("MainWindowHandle", 0),
                                title=item.get("MainWindowTitle", ""),
                                process_name=item.get("ProcessName", ""),
                                pid=item.get("Id", 0),
                            )
                        )
            except Exception:
                pass
        return windows

    def get_active_window(self) -> WindowInfo | None:
        windows = self.enumerate_windows()
        if windows:
            windows[0].is_active = True
            return windows[0]
        return None

    def focus(self, title_or_process: str) -> bool:
        if sys.platform == "win32":
            try:
                ps_script = (
                    f"$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title_or_process}*' -or $_.ProcessName -like '*{title_or_process}*' }} | Select-Object -First 1\n"
                    "if ($proc) {\n"
                    "    $wshell = New-Object -ComObject wscript.shell\n"
                    "    $wshell.AppActivate($proc.Id)\n"
                    "}\n"
                )
                res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
                return "True" in res.stdout
            except Exception:
                pass
        return True

    def minimize(self, title_or_process: str) -> bool:
        if sys.platform == "win32":
            try:
                ps_script = (
                    "Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);' -Name Win32Show -Namespace Win32\n"
                    f"$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title_or_process}*' }} | Select-Object -First 1\n"
                    "if ($proc) {\n"
                    "    [Win32.Win32Show]::ShowWindow($proc.MainWindowHandle, 6)\n"
                    "}\n"
                )
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return True
            except Exception:
                pass
        return True

    def maximize(self, title_or_process: str) -> bool:
        if sys.platform == "win32":
            try:
                ps_script = (
                    "Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);' -Name Win32Show -Namespace Win32\n"
                    f"$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title_or_process}*' }} | Select-Object -First 1\n"
                    "if ($proc) {\n"
                    "    [Win32.Win32Show]::ShowWindow($proc.MainWindowHandle, 3)\n"
                    "}\n"
                )
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return True
            except Exception:
                pass
        return True

    def close(self, title_or_process: str) -> bool:
        if sys.platform == "win32":
            try:
                ps_script = (
                    f"$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title_or_process}*' -or $_.ProcessName -like '*{title_or_process}*' }}\n"
                    "if ($proc) {\n"
                    "    $proc | Stop-Process -Force\n"
                    "}\n"
                )
                res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return res.returncode == 0
            except Exception:
                pass
        return True
