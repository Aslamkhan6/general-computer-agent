from pathlib import Path


from app.core.state import ActionResult
from app.core.enums import ActionStatus
from .base import BaseTool


class CreateDirectoryTool(BaseTool):
    name = "create_directory"

    description = (
        "Create a directory at the specified path. "
        "The operation succeeds if the directory already exists."
    )

    def execute(self, path: str) -> ActionResult:
        try:
            directory = Path(path)

            directory.mkdir(parents=True, exist_ok=True)

            return ActionResult(
                status="SUCCESS",
                output={
                    "path": str(directory.resolve()),
                    "exists": directory.exists(),
                    "is_directory": directory.is_dir(),
                },
            )

        except Exception as exc:
            return ActionResult(
                status="FAILED",
                error=str(exc),
            )