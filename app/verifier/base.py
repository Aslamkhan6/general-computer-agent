from abc import ABC, abstractmethod
from typing import Any


class BaseVerifier(ABC):

    @abstractmethod
    def verify(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
    ) -> bool:
        pass