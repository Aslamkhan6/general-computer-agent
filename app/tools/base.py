from abc import ABC, abstractmethod
from typing import Any

from app.core.state import ActionResult


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> ActionResult:
        pass