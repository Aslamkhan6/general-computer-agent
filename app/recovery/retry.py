import time
from dataclasses import dataclass, field
from typing import Any
from app.core.enums import ActionStatus
from app.core.state import ActionResult, TaskStep
from app.observer.base import BaseObserver
from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest
from app.verifier.base import BaseVerifier
from .models import FailureCategory, FailureReport


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    delay_seconds: float = 0.1
    backoff_factor: float = 1.5
    retryable_categories: set[FailureCategory] = field(
        default_factory=lambda: {
            FailureCategory.TRANSIENT,
            FailureCategory.TIMEOUT,
            FailureCategory.TOOL,
            FailureCategory.VERIFICATION,
        }
    )


class RetryEngine:
    """Executes controlled retry strategies for failure recovery."""

    def __init__(self, policy: RetryPolicy | None = None):
        self.policy = policy or RetryPolicy()

    def is_retryable(self, category: FailureCategory, attempt_count: int) -> bool:
        return category in self.policy.retryable_categories and attempt_count < self.policy.max_attempts

    def execute_retry(
        self,
        step: TaskStep,
        executor: ToolExecutor,
        observer: BaseObserver,
        verifier: BaseVerifier,
        attempt_number: int = 1,
    ) -> tuple[bool, ActionResult | None, dict[str, Any] | None]:
        delay = self.policy.delay_seconds * (self.policy.backoff_factor ** (attempt_number - 1))
        time.sleep(min(delay, 0.5))

        req = ToolRequest(tool_name=step.tool_name, arguments=step.input_data)
        res = executor.execute(req)

        if res.status != ActionStatus.SUCCESS:
            return False, res, None

        obs_path = step.input_data.get("path", "")
        actual_state = observer.observe(path=obs_path)
        verified = verifier.verify(expected=step.expected_state, actual=actual_state)

        return verified, res, actual_state
