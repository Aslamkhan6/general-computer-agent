from abc import ABC, abstractmethod
from typing import Any

from app.core.enums import RiskLevel
from app.core.state import ActionResult


class BaseTool(ABC):
    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    parameters: dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs: Any) -> ActionResult:
        pass