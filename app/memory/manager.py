from typing import Any
from app.core.state import AgentTask
from .importance import ImportanceScorer, MemoryPruner
from .long_term import LongTermMemory
from .models import Memory, MemorySource, MemoryType
from .retrieval import MemoryRetrievalEngine
from .short_term import ShortTermMemory
from .skills.manager import SkillManager
from .storage import MemoryStorage


class MemoryManager:
    """Unified Memory Orchestrator managing Short-Term Context, Long-Term Persistence, Relevance Retrieval, Importance Scoring, Pruning, and Skills."""

    def __init__(
        self,
        db_path: str = "./workspace/memory/memories.db",
        skill_manager: SkillManager | None = None,
    ):
        self.storage = MemoryStorage(db_path=db_path)
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage=self.storage)
        self.retrieval_engine = MemoryRetrievalEngine()
        self.importance_scorer = ImportanceScorer()
        self.pruner = MemoryPruner()
        self.skills = skill_manager or SkillManager()

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.USER_PREFERENCE,
        source: MemorySource = MemorySource.USER,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        importance = self.importance_scorer.score(content, memory_type)
        is_persistent = importance >= 0.6 or memory_type in (
            MemoryType.USER_PREFERENCE,
            MemoryType.USER_FACT,
            MemoryType.TASK_HISTORY,
            MemoryType.IMPORTANT_EVENT,
        )

        mem = Memory(
            content=content,
            type=memory_type,
            source=source,
            importance=importance,
            persistent=is_persistent,
            metadata=metadata or {},
        )

        self.short_term.add_event(content, memory_type=memory_type, metadata=metadata)
        if is_persistent:
            self.long_term.add(mem)

        return mem

    def retrieve_relevant_context(self, user_query: str, top_k: int = 3) -> dict[str, Any]:
        all_mems = self.long_term.all_memories()
        relevant_memories = self.retrieval_engine.retrieve(user_query, candidates=all_mems, top_k=top_k)
        matching_skill = self.skills.select_skill(user_query)

        return {
            "query": user_query,
            "relevant_memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "type": m.type.value,
                    "importance": m.importance,
                }
                for m in relevant_memories
            ],
            "matching_skill": matching_skill.name if matching_skill else None,
            "short_term_context": self.short_term.get_context(),
        }

    def record_task_completion(self, task: AgentTask) -> None:
        content = f"Completed task '{task.user_request}' with status {task.status.value}."
        meta = {"task_id": task.id, "steps_count": len(task.steps), "final_result": task.final_result}
        self.remember(
            content=content,
            memory_type=MemoryType.TASK_HISTORY,
            source=MemorySource.AGENT,
            metadata=meta,
        )

    def prune(self) -> int:
        all_mems = self.long_term.all_memories()
        retained = self.pruner.prune(all_mems)
        pruned_count = len(all_mems) - len(retained)
        # Clear storage and resave retained
        for m in all_mems:
            if m not in retained:
                self.long_term.delete(m.id)
        return pruned_count
