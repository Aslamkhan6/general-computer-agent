from dataclasses import dataclass, field
from typing import Any


@dataclass
class CircuitBreakerStatus:
    is_tripped: bool = False
    failure_count: int = 0
    max_threshold: int = 3
    reason: str | None = None


class CircuitBreaker:
    """Protects system against infinite recovery loops by enforcing recovery attempt thresholds."""

    def __init__(self, max_failures_per_step: int = 3):
        self.max_failures_per_step = max_failures_per_step
        self._step_failures: dict[str, int] = {}

    def record_attempt(self, step_id: str) -> CircuitBreakerStatus:
        current = self._step_failures.get(step_id, 0) + 1
        self._step_failures[step_id] = current

        if current >= self.max_failures_per_step:
            return CircuitBreakerStatus(
                is_tripped=True,
                failure_count=current,
                max_threshold=self.max_failures_per_step,
                reason=f"Step '{step_id}' exceeded max recovery attempts ({self.max_failures_per_step}).",
            )

        return CircuitBreakerStatus(
            is_tripped=False,
            failure_count=current,
            max_threshold=self.max_failures_per_step,
        )

    def is_tripped(self, step_id: str) -> bool:
        return self._step_failures.get(step_id, 0) >= self.max_failures_per_step

    def reset(self, step_id: str | None = None) -> None:
        if step_id:
            self._step_failures.pop(step_id, None)
        else:
            self._step_failures.clear()
