import re
from typing import Any
from .models import Memory, MemoryType


class MemoryRetrievalEngine:
    """Calculates relevance scores and retrieves top matching memories for a user query."""

    def extract_keywords(self, text: str) -> list[str]:
        words = re.findall(r"\w+", text.lower())
        stopwords = {"a", "an", "the", "in", "on", "of", "to", "for", "is", "my", "me", "my", "us", "called", "create", "make"}
        return [w for w in words if w not in stopwords]

    def compute_relevance(self, query_keywords: list[str], memory: Memory) -> float:
        content_words = set(re.findall(r"\w+", memory.content.lower()))
        if not content_words or not query_keywords:
            overlap = 0.0
        else:
            matches = sum(1 for k in query_keywords if k in content_words)
            overlap = matches / max(len(query_keywords), 1)

        # Weighted combination: term overlap (50%), importance (30%), recency/access (20%)
        type_bonus = 0.2 if memory.type in (MemoryType.USER_PREFERENCE, MemoryType.LEARNED_PATTERN) else 0.0
        score = (overlap * 0.5) + (memory.importance * 0.3) + type_bonus
        return min(score, 1.0)

    def retrieve(self, query: str, candidates: list[Memory], top_k: int = 3, threshold: float = 0.15) -> list[Memory]:
        keywords = self.extract_keywords(query)
        scored = []
        for mem in candidates:
            rel = self.compute_relevance(keywords, mem)
            if rel >= threshold:
                scored.append((rel, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for _, mem in scored[:top_k]:
            mem.touch()
            results.append(mem)
        return results
