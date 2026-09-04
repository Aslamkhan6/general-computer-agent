import os
import shutil
import unittest

from app.agent.controller import AgentController
from app.core.events import EventBus
from app.observer.filesystem import FilesystemObserver
from app.recovery.manager import RecoveryEngine
from app.security.manager import SecurityManager
from app.supervisor import (
    AgentRegistry,
    AgentRole,
    AgentStatus,
    HealthMonitor,
    MessageBus,
    ResourceManager,
    ResultManager,
    SharedTaskContextManager,
    SubTask,
    Supervisor,
    SupervisorState,
    TaskDispatcher,
    TaskScheduler,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier


class TestModule9Supervisor(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()

        self.security_manager = SecurityManager()
        self.recovery_engine = RecoveryEngine()
        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
            recovery_engine=self.recovery_engine,
            security_manager=self.security_manager,
        )

        self.supervisor = Supervisor(
            controller=self.controller,
            security_manager=self.security_manager,
            recovery_engine=self.recovery_engine,
        )

    def test_9_1_agent_registry_and_discovery(self):
        reg = AgentRegistry()
        agents = reg.list_agents()
        self.assertGreaterEqual(len(agents), 5)

        coder = reg.find_agent_by_role(AgentRole.CODING)
        self.assertIsNotNone(coder)
        self.assertEqual(coder.name, "CodingAgent")

    def test_9_2_task_dispatcher(self):
        dispatcher = TaskDispatcher(registry=self.supervisor.registry)
        subtask = SubTask(parent_task_id="t1", description="Write Python file", assigned_role=AgentRole.CODING, required_capabilities=["write_file"])
        worker = dispatcher.dispatch(subtask)
        self.assertEqual(worker.role, AgentRole.CODING)
        self.assertEqual(worker.status, AgentStatus.ASSIGNED)

    def test_9_3_message_bus_and_context(self):
        bus = MessageBus()
        msg = bus.send_message("agent-coding-01", "SUPERVISOR", "t1", "Subtask completed", payload={"file": "main.py"})
        self.assertEqual(msg.sender_id, "agent-coding-01")

        ctx_mgr = SharedTaskContextManager()
        ctx_mgr.init_context("t1", "Build Project")
        ctx_mgr.record_subtask_result("t1", "sub-1", {"status": "SUCCESS"}, artifacts=["main.py"])
        ctx = ctx_mgr.get_context("t1")
        self.assertIn("main.py", ctx["shared_artifacts"])

    def test_9_4_resource_manager(self):
        rm = ResourceManager()
        locked, msg1 = rm.acquire_lock("./workspace/file.txt", "agent-1")
        self.assertTrue(locked)

        # Conflict check for another agent
        locked2, msg2 = rm.acquire_lock("./workspace/file.txt", "agent-2")
        self.assertFalse(locked2)
        self.assertIn("locked by agent 'agent-1'", msg2)

        rm.release_lock("./workspace/file.txt", "agent-1")
        self.assertFalse(rm.is_locked("./workspace/file.txt"))

    def test_9_5_supervisor_end_to_end_multi_agent_execution(self):
        if os.path.exists("./workspace/custom_projects/project_app"):
            shutil.rmtree("./workspace/custom_projects/project_app", ignore_errors=True)

        user_goal = "Create a python project called project_app"
        aggregated = self.supervisor.run_supervisor_task(user_goal, task_id="task-sup-test-101")

        self.assertEqual(self.supervisor.state, SupervisorState.COMPLETED)
        self.assertEqual(aggregated["status"], AgentStatus.COMPLETED)
        self.assertGreaterEqual(aggregated["subtasks_completed"], 2)
        self.assertTrue(aggregated["verified"])

        shutil.rmtree("./workspace/custom_projects/project_app", ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
