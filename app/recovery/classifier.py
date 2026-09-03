import re
from .models import FailureCategory, FailureReport


class FailureClassifier:
    """Classifies error messages and failure reports into distinct categories."""

    def classify(self, report: FailureReport) -> FailureCategory:
        err = report.error_message.lower()

        if any(term in err for term in ["permission", "access denied", "unauthorized", "forbidden"]):
            return FailureCategory.PERMISSION
        elif any(term in err for term in ["timeout", "timed out", "time out"]):
            return FailureCategory.TIMEOUT
        elif any(term in err for term in ["not found", "does not exist", "no such file"]):
            return FailureCategory.NOT_FOUND
        elif any(term in err for term in ["transient", "network", "connection reset", "temporary"]):
            return FailureCategory.TRANSIENT
        elif any(term in err for term in ["validation", "invalid argument", "schema"]):
            return FailureCategory.VALIDATION
        elif any(term in err for term in ["verification failed", "expected state"]):
            return FailureCategory.VERIFICATION
        elif any(term in err for term in ["environment", "incompatible", "python version"]):
            return FailureCategory.ENVIRONMENT

        return report.category or FailureCategory.TOOL
