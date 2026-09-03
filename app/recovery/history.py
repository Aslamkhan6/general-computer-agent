from typing import Any
from .models import FailureReport, RecoveryRecord


class RecoveryHistory:
    """Maintains an audit trail of failure reports, recovery strategies attempted, and outcomes."""

    def __init__(self):
        self._reports: list[FailureReport] = []
        self._records: list[RecoveryRecord] = []

    def log_failure(self, report: FailureReport) -> None:
        self._reports.append(report)

    def log_recovery(self, record: RecoveryRecord) -> None:
        self._records.append(record)

    def get_task_history(self, task_id: str) -> list[RecoveryRecord]:
        return [r for r in self._records if r.task_id == task_id]

    def get_all_records(self) -> list[RecoveryRecord]:
        return list(self._records)

    def clear(self) -> None:
        self._reports.clear()
        self._records.clear()
