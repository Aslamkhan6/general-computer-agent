import re
from datetime import datetime, timezone
from .models import Memory, MemoryType


class ImportanceScorer:
    """Calculates deterministic importance scores for memories."""

    HIGH_PRIORITY_PATTERNS = [
        r"\bremember\b",
        r"\balways\b",
        r"\bprefer\b",
        r"\bnever\b",
        r"\bmy usual\b",
        r"\bstore in\b",
        r"\bprojects go\b",
    ]

    def score(self, content: str, memory_type: MemoryType) -> float:
        lower = content.lower()

        # Check explicit user preference signals
        for pattern in self.HIGH_PRIORITY_PATTERNS:
            if re.search(pattern, lower):
                return 0.95

        if memory_type == MemoryType.USER_PREFERENCE:
            return 0.90
        elif memory_type == MemoryType.USER_FACT:
            return 0.85
        elif memory_type == MemoryType.LEARNED_PATTERN:
            return 0.80
        elif memory_type == MemoryType.PROJECT_CONTEXT:
            return 0.65
        elif memory_type == MemoryType.IMPORTANT_EVENT:
            return 0.75

        return 0.40


class MemoryPruner:
    """Prunes expired, low-importance, or stale memories."""

    def prune(self, memories: list[Memory], min_importance: float = 0.25, max_age_days: int = 90) -> list[Memory]:
        now = datetime.now(timezone.utc)
        retained = []
        for mem in memories:
            if mem.persistent and mem.importance >= 0.8:
                retained.append(mem)
                continue

            # Check expiration
            if mem.expiration and mem.expiration <= now:
                continue

            # Check low importance and age
            age_days = (now - mem.timestamp).days
            if mem.importance < min_importance and age_days > 7 and mem.access_count < 2:
                continue

            if age_days > max_age_days and mem.access_count < 3 and mem.importance < 0.7:
                continue

            retained.append(mem)

        return retained
