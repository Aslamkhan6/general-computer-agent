import os
import subprocess
import sys
from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


class ExecuteCommandTool(BaseTool):
    name = "execute_command"
    description = "Execute a shell command safely within a specified working directory."
    risk_level = RiskLevel.HIGH
    parameters = {"command": "string", "cwd": "string (optional)", "timeout": "integer (optional, default 60)"}

    def execute(self, command: str, cwd: str | None = None, timeout: int = 60) -> ActionResult:
        try:
            working_dir = cwd or os.getcwd()
            res = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            status = ActionStatus.SUCCESS if res.returncode == 0 else ActionStatus.FAILED
            return ActionResult(
                status=status,
                output={
                    "command": command,
                    "returncode": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip(),
                },
                error=res.stderr.strip() if res.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return ActionResult(status=ActionStatus.FAILED, error=f"Command timed out after {timeout} seconds")
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class RunPowerShellTool(BaseTool):
    name = "run_powershell"
    description = "Run a PowerShell script or command."
    risk_level = RiskLevel.HIGH
    parameters = {"script": "string", "cwd": "string (optional)", "timeout": "integer (optional, default 60)"}

    def execute(self, script: str, cwd: str | None = None, timeout: int = 60) -> ActionResult:
        try:
            working_dir = cwd or os.getcwd()
            ps_cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]
            res = subprocess.run(
                ps_cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            status = ActionStatus.SUCCESS if res.returncode == 0 else ActionStatus.FAILED
            return ActionResult(
                status=status,
                output={
                    "script": script,
                    "returncode": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip(),
                },
                error=res.stderr.strip() if res.returncode != 0 else None,
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class StartProcessTool(BaseTool):
    name = "start_process"
    description = "Start a background process."
    risk_level = RiskLevel.MEDIUM
    parameters = {"command": "string", "cwd": "string (optional)"}

    def execute(self, command: str, cwd: str | None = None) -> ActionResult:
        try:
            working_dir = cwd or os.getcwd()
            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"pid": proc.pid, "command": command, "started": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class StopProcessTool(BaseTool):
    name = "stop_process"
    description = "Stop/kill a process by PID."
    risk_level = RiskLevel.HIGH
    parameters = {"pid": "integer"}

    def execute(self, pid: int) -> ActionResult:
        try:
            if sys.platform == "win32":
                res = subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True, text=True)
            else:
                res = subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True, text=True)

            if res.returncode == 0:
                return ActionResult(status=ActionStatus.SUCCESS, output={"pid": pid, "stopped": True})
            else:
                return ActionResult(status=ActionStatus.FAILED, error=res.stderr.strip())
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetProcessTool(BaseTool):
    name = "get_process"
    description = "Query running processes matching a name or get process list."
    risk_level = RiskLevel.LOW
    parameters = {"name": "string (optional)"}

    def execute(self, name: str | None = None) -> ActionResult:
        try:
            if sys.platform == "win32":
                cmd = f"tasklist /FI \"IMAGENAME eq {name}\"" if name else "tasklist"
            else:
                cmd = f"ps aux | grep {name}" if name else "ps aux"

            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"query": name, "raw_output": res.stdout.strip()},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class InstallPackageTool(BaseTool):
    name = "install_package"
    description = "Install a package via pip or npm."
    risk_level = RiskLevel.HIGH
    parameters = {"package_name": "string", "manager": "string (pip | npm, default pip)"}

    def execute(self, package_name: str, manager: str = "pip") -> ActionResult:
        try:
            if manager.lower() == "pip":
                cmd = f"{sys.executable} -m pip install {package_name}"
            elif manager.lower() == "npm":
                cmd = f"npm install {package_name}"
            else:
                return ActionResult(status=ActionStatus.FAILED, error=f"Unsupported package manager: {manager}")

            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            status = ActionStatus.SUCCESS if res.returncode == 0 else ActionStatus.FAILED
            return ActionResult(
                status=status,
                output={"package": package_name, "manager": manager, "stdout": res.stdout.strip()},
                error=res.stderr.strip() if res.returncode != 0 else None,
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
