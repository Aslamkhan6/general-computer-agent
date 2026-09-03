import os
import subprocess
from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


def _run_git_cmd(args: list[str], cwd: str | None = None) -> ActionResult:
    try:
        working_dir = cwd or os.getcwd()
        cmd = ["git"] + args
        res = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
        )
        status = ActionStatus.SUCCESS if res.returncode == 0 else ActionStatus.FAILED
        return ActionResult(
            status=status,
            output={
                "command": " ".join(cmd),
                "returncode": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
            },
            error=res.stderr.strip() if res.returncode != 0 else None,
        )
    except Exception as exc:
        return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GitInitTool(BaseTool):
    name = "git_init"
    description = "Initialize a new Git repository."
    risk_level = RiskLevel.LOW
    parameters = {"cwd": "string (optional)"}

    def execute(self, cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["init"], cwd=cwd)


class GitStatusTool(BaseTool):
    name = "git_status"
    description = "Check working tree status."
    risk_level = RiskLevel.LOW
    parameters = {"cwd": "string (optional)"}

    def execute(self, cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["status", "--short"], cwd=cwd)


class GitAddTool(BaseTool):
    name = "git_add"
    description = "Add file contents to the staging index."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string (optional, default .)", "cwd": "string (optional)"}

    def execute(self, path: str = ".", cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["add", path], cwd=cwd)


class GitCommitTool(BaseTool):
    name = "git_commit"
    description = "Record changes to the repository with a commit message."
    risk_level = RiskLevel.MEDIUM
    parameters = {"message": "string", "cwd": "string (optional)"}

    def execute(self, message: str, cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["commit", "-m", message], cwd=cwd)


class GitBranchTool(BaseTool):
    name = "git_branch"
    description = "List, create, or delete branches."
    risk_level = RiskLevel.LOW
    parameters = {"name": "string (optional)", "cwd": "string (optional)"}

    def execute(self, name: str | None = None, cwd: str | None = None) -> ActionResult:
        args = ["branch", name] if name else ["branch"]
        return _run_git_cmd(args, cwd=cwd)


class GitCheckoutTool(BaseTool):
    name = "git_checkout"
    description = "Switch branches or restore working tree files."
    risk_level = RiskLevel.MEDIUM
    parameters = {"target": "string", "create_new": "boolean (optional, -b flag)", "cwd": "string (optional)"}

    def execute(self, target: str, create_new: bool = False, cwd: str | None = None) -> ActionResult:
        args = ["checkout", "-b", target] if create_new else ["checkout", target]
        return _run_git_cmd(args, cwd=cwd)


class GitPullTool(BaseTool):
    name = "git_pull"
    description = "Fetch from and integrate with another repository or a local branch."
    risk_level = RiskLevel.MEDIUM
    parameters = {"remote": "string (optional, default origin)", "branch": "string (optional)", "cwd": "string (optional)"}

    def execute(self, remote: str = "origin", branch: str | None = None, cwd: str | None = None) -> ActionResult:
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return _run_git_cmd(args, cwd=cwd)


class GitPushTool(BaseTool):
    name = "git_push"
    description = "Update remote refs along with associated objects."
    risk_level = RiskLevel.HIGH
    parameters = {"remote": "string (optional, default origin)", "branch": "string (optional)", "cwd": "string (optional)"}

    def execute(self, remote: str = "origin", branch: str | None = None, cwd: str | None = None) -> ActionResult:
        args = ["push", remote]
        if branch:
            args.append(branch)
        return _run_git_cmd(args, cwd=cwd)


class GitCloneTool(BaseTool):
    name = "git_clone"
    description = "Clone a repository into a new directory."
    risk_level = RiskLevel.MEDIUM
    parameters = {"url": "string", "destination": "string (optional)", "cwd": "string (optional)"}

    def execute(self, url: str, destination: str | None = None, cwd: str | None = None) -> ActionResult:
        args = ["clone", url]
        if destination:
            args.append(destination)
        return _run_git_cmd(args, cwd=cwd)


class GitDiffTool(BaseTool):
    name = "git_diff"
    description = "Show changes between commits, commit and working tree, etc."
    risk_level = RiskLevel.LOW
    parameters = {"cwd": "string (optional)"}

    def execute(self, cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["diff"], cwd=cwd)


class GitLogTool(BaseTool):
    name = "git_log"
    description = "Show commit logs."
    risk_level = RiskLevel.LOW
    parameters = {"max_count": "integer (optional, default 10)", "cwd": "string (optional)"}

    def execute(self, max_count: int = 10, cwd: str | None = None) -> ActionResult:
        return _run_git_cmd(["log", f"-n{max_count}", "--oneline"], cwd=cwd)
