from pathlib import Path
from typing import Any

from .base import BaseObserver


class FilesystemObserver(BaseObserver):

    def observe(self, path: str) -> dict[str, Any]:
        target = Path(path)

        return {
            "path": str(target.resolve()),
            "exists": target.exists(),
            "is_file": target.is_file(),
            "is_directory": target.is_dir(),
        }