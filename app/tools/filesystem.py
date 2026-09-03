import os
import shutil
from pathlib import Path
from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file as text."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string", "encoding": "string (optional, default utf-8)"}

    def execute(self, path: str, encoding: str = "utf-8") -> ActionResult:
        try:
            target = Path(path)
            if not target.is_file():
                return ActionResult(
                    status=ActionStatus.FAILED,
                    error=f"File not found or is not a file: {path}",
                )
            content = target.read_text(encoding=encoding)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"path": str(target.resolve()), "content": content, "size": target.stat().st_size},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file at the specified path."
    risk_level = RiskLevel.MEDIUM
    parameters = {"path": "string", "content": "string", "append": "boolean (optional)"}

    def execute(self, path: str, content: str, append: bool = False) -> ActionResult:
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            with open(target, mode, encoding="utf-8") as f:
                f.write(content)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"path": str(target.resolve()), "size": target.stat().st_size, "appended": append},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class CreateFileTool(BaseTool):
    name = "create_file"
    description = "Create an empty file if it does not already exist."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string"}

    def execute(self, path: str) -> ActionResult:
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.touch()
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"path": str(target.resolve()), "created": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class CreateDirectoryTool(BaseTool):
    name = "create_directory"
    description = "Create a directory at the specified path."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string"}

    def execute(self, path: str) -> ActionResult:
        try:
            directory = Path(path)
            directory.mkdir(parents=True, exist_ok=True)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={
                    "path": str(directory.resolve()),
                    "exists": directory.exists(),
                    "is_directory": directory.is_dir(),
                },
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a single file from disk."
    risk_level = RiskLevel.HIGH
    parameters = {"path": "string"}

    def execute(self, path: str) -> ActionResult:
        try:
            target = Path(path)
            if not target.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"File does not exist: {path}")
            if target.is_dir():
                return ActionResult(status=ActionStatus.FAILED, error=f"Target is a directory, not a file: {path}")
            target.unlink()
            return ActionResult(status=ActionStatus.SUCCESS, output={"path": str(target.resolve()), "deleted": True})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class DeleteDirectoryTool(BaseTool):
    name = "delete_directory"
    description = "Delete a directory and all of its contents."
    risk_level = RiskLevel.CRITICAL
    parameters = {"path": "string", "recursive": "boolean (optional, default True)"}

    def execute(self, path: str, recursive: bool = True) -> ActionResult:
        try:
            target = Path(path)
            if not target.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"Directory does not exist: {path}")
            if not target.is_dir():
                return ActionResult(status=ActionStatus.FAILED, error=f"Target is not a directory: {path}")
            if recursive:
                shutil.rmtree(target)
            else:
                target.rmdir()
            return ActionResult(status=ActionStatus.SUCCESS, output={"path": str(target.resolve()), "deleted": True})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class CopyTool(BaseTool):
    name = "copy"
    description = "Copy a file or directory to a destination path."
    risk_level = RiskLevel.MEDIUM
    parameters = {"source": "string", "destination": "string"}

    def execute(self, source: str, destination: str) -> ActionResult:
        try:
            src, dst = Path(source), Path(destination)
            if not src.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"Source does not exist: {source}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"source": str(src.resolve()), "destination": str(dst.resolve()), "copied": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class MoveTool(BaseTool):
    name = "move"
    description = "Move a file or directory to a destination path."
    risk_level = RiskLevel.MEDIUM
    parameters = {"source": "string", "destination": "string"}

    def execute(self, source: str, destination: str) -> ActionResult:
        try:
            src, dst = Path(source), Path(destination)
            if not src.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"Source does not exist: {source}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"source": str(src.resolve()), "destination": str(dst.resolve()), "moved": True},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class RenameTool(BaseTool):
    name = "rename"
    description = "Rename a file or directory."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string", "new_name": "string"}

    def execute(self, path: str, new_name: str) -> ActionResult:
        try:
            target = Path(path)
            if not target.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"Path does not exist: {path}")
            new_path = target.parent / new_name
            target.rename(new_path)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"old_path": str(target.resolve()), "new_path": str(new_path.resolve())},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List all files and subdirectories in a directory."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string"}

    def execute(self, path: str) -> ActionResult:
        try:
            target = Path(path)
            if not target.is_dir():
                return ActionResult(status=ActionStatus.FAILED, error=f"Path is not a directory: {path}")
            items = []
            for item in target.iterdir():
                items.append({
                    "name": item.name,
                    "is_directory": item.is_dir(),
                    "is_file": item.is_file(),
                    "size": item.stat().st_size if item.is_file() else None,
                })
            return ActionResult(status=ActionStatus.SUCCESS, output={"path": str(target.resolve()), "items": items})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files matching a pattern in a directory."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string", "pattern": "string (glob pattern, default *)"}

    def execute(self, path: str, pattern: str = "*") -> ActionResult:
        try:
            target = Path(path)
            if not target.is_dir():
                return ActionResult(status=ActionStatus.FAILED, error=f"Path is not a directory: {path}")
            matches = [str(p.resolve()) for p in target.glob(pattern)]
            return ActionResult(status=ActionStatus.SUCCESS, output={"path": str(target.resolve()), "pattern": pattern, "matches": matches})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class GetMetadataTool(BaseTool):
    name = "get_metadata"
    description = "Get detailed file/directory metadata."
    risk_level = RiskLevel.LOW
    parameters = {"path": "string"}

    def execute(self, path: str) -> ActionResult:
        try:
            target = Path(path)
            if not target.exists():
                return ActionResult(status=ActionStatus.FAILED, error=f"Path does not exist: {path}")
            stat = target.stat()
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={
                    "path": str(target.resolve()),
                    "exists": True,
                    "is_file": target.is_file(),
                    "is_directory": target.is_dir(),
                    "size": stat.st_size,
                    "created_at": stat.st_ctime,
                    "modified_at": stat.st_mtime,
                },
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))