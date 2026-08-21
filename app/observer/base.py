from abc import ABC, abstractmethod
from typing import Any


class BaseObserver(ABC):

    @abstractmethod
    def observe(self, **kwargs: Any) -> dict[str, Any]:
        pass