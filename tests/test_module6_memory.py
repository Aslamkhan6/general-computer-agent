import os
import shutil
import unittest

from app.agent.controller import AgentController
from app.core.enums import ActionStatus, StepStatus, TaskStatus
from app.core.events import EventBus
from app.memory import (
    Memory,
    MemoryManager,
    MemorySource,
    MemoryType,
    ShortTermMemory,
    LongTermMemory,
    MemoryStorage,
    MemoryRetrievalEngine,
    ImportanceScorer,
    MemoryPruner,
)
from app.memory.skills import (
    Skill,
    SkillInput,
    SkillStep,
    SkillRegistry,
    SkillExecutor,
    SkillManager,
)
from app.observer.filesystem import FilesystemObserver
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier


class TestModule6Memory(unittest.TestCase):

    def setUp(self):
        self.db_path = "./workspace/test_memory/memories.db"
        if os.path.exists("./workspace/test_memory"):
            shutil.rmtree("./workspace/test_memory", ignore_errors=True)

        self.event_bus = EventBus()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()

        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
        )

        self.skill_manager = SkillManager(controller=self.controller)
        self.memory_manager = MemoryManager(db_path=self.db_path, skill_manager=self.skill_manager)

    def tearDown(self):
        if os.path.exists("./workspace/test_memory"):
            shutil.rmtree("./workspace/test_memory", ignore_errors=True)

    def test_6_1_memory_models(self):
        mem = Memory(content="User prefers dark theme", type=MemoryType.USER_PREFERENCE, importance=0.9, persistent=True)
        self.assertEqual(mem.content, "User prefers dark theme")
        self.assertEqual(mem.type, MemoryType.USER_PREFERENCE)
        self.assertTrue(mem.persistent)
        mem.touch()
        self.assertEqual(mem.access_count, 1)

    def test_6_2_short_term_memory(self):
        st = ShortTermMemory()
        st.add_event("Create directory Projects", metadata={"path": "./workspace/Projects"})
        ctx = st.get_context()
        self.assertEqual(ctx["last_directory"], "./workspace/Projects")
        self.assertEqual(ctx["last_operation"], "create_directory")

    def test_6_4_storage_sqlite(self):
        storage = MemoryStorage(db_path=self.db_path)
        mem = Memory(id="m101", content="Test SQLite memory", type=MemoryType.USER_FACT, importance=0.8, persistent=True)
        storage.save(mem)

        loaded = storage.get("m101")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.content, "Test SQLite memory")

        all_mems = storage.load_all()
        self.assertGreaterEqual(len(all_mems), 1)

    def test_6_5_retrieval_engine(self):
        storage = MemoryStorage(db_path=self.db_path)
        lt = LongTermMemory(storage=storage)

        mem1 = Memory(id="m1", content="User prefers Python projects in ./workspace/projects", type=MemoryType.USER_PREFERENCE, importance=0.95, persistent=True)
        mem2 = Memory(id="m2", content="User likes Node.js applications", type=MemoryType.USER_PREFERENCE, importance=0.7, persistent=True)
        lt.add(mem1)
        lt.add(mem2)

        engine = MemoryRetrievalEngine()
        results = engine.retrieve("usual Python project", candidates=lt.all_memories(), top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "m1")

    def test_6_6_importance_and_pruning(self):
        scorer = ImportanceScorer()
        score = scorer.score("Always store my projects in ./workspace/my_projects", MemoryType.USER_PREFERENCE)
        self.assertGreaterEqual(score, 0.9)

        pruner = MemoryPruner()
        mem_high = Memory(content="High priority", importance=0.9, persistent=True)
        mem_low = Memory(content="Temporary one-off action", importance=0.1, persistent=False)
        retained = pruner.prune([mem_high, mem_low], min_importance=0.25)
        self.assertIn(mem_high, retained)

    def test_6_8_skill_system(self):
        skills_list = self.skill_manager.list_available_skills()
        self.assertGreaterEqual(len(skills_list), 1)
        skill_names = [s["name"] for s in skills_list]
        self.assertIn("create_python_project", skill_names)

        matched = self.skill_manager.select_skill("Create a python project called AI-Skill-Test")
        self.assertIsNotNone(matched)
        self.assertEqual(matched.name, "create_python_project")

    def test_6_14_complete_definition_of_done(self):
        # 1. User sets preference memory
        pref_mem = self.memory_manager.remember(
            content="User prefers Python projects inside ./workspace/custom_projects",
            memory_type=MemoryType.USER_PREFERENCE,
            source=MemorySource.USER,
        )
        self.assertIsNotNone(pref_mem.id)

        # 2. Retrieve memory & select skill for new user request
        user_request = "Create my usual Python project called AI-Assistant"
        ctx = self.memory_manager.retrieve_relevant_context(user_request)
        self.assertEqual(ctx["matching_skill"], "create_python_project")
        self.assertGreaterEqual(len(ctx["relevant_memories"]), 1)

        # 3. Execute Skill via SkillManager & AgentController
        task = self.skill_manager.execute_skill_by_name(
            skill_name="create_python_project",
            inputs={"project_name": "AI-Assistant", "parent_dir": "./workspace/custom_projects"},
            task_id="dod-task-001",
        )

        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(len(task.steps), 4)

        # Verify created project filesystem artifacts
        proj_base = "./workspace/custom_projects/AI-Assistant"
        self.assertTrue(os.path.exists(f"{proj_base}/src"))
        self.assertTrue(os.path.exists(f"{proj_base}/tests"))
        self.assertTrue(os.path.exists(f"{proj_base}/README.md"))
        self.assertTrue(os.path.exists(f"{proj_base}/requirements.txt"))

        # 4. Record task completion in memory
        self.memory_manager.record_task_completion(task)
        history = self.memory_manager.long_term.get_by_type(MemoryType.TASK_HISTORY)
        self.assertGreaterEqual(len(history), 1)

        # Clean up created directory
        shutil.rmtree("./workspace/custom_projects", ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
