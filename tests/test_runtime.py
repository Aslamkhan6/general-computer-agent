import os
import shutil
import unittest

from app.agent.controller import AgentController
from app.core.enums import StepStatus, TaskStatus
from app.core.events import EventBus, EventType
from app.core.exceptions import PlanningError
from app.core.state import AgentTask
from app.observer.filesystem import FilesystemObserver
from app.planner.planner import Planner
from app.tools.executor import ToolExecutor
from app.tools.filesystem import CreateDirectoryTool
from app.tools.registry import ToolRegistry
from app.verifier.filesystem import FilesystemVerifier


class TestRuntime(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.events = []
        self.event_bus.subscribe(lambda e: self.events.append(e))

        self.registry = ToolRegistry()
        self.registry.register(CreateDirectoryTool())

        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()

        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
        )
        self.planner = Planner()

    def test_planner_valid_goal(self):
        plan = self.planner.create_plan("Create a directory called test_dir_001")
        self.assertEqual(plan.goal, "Create a directory called test_dir_001")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].tool_name, "create_directory")
        self.assertEqual(plan.steps[0].input_data["path"], "./workspace/test_dir_001")

    def test_planner_invalid_goal(self):
        with self.assertRaises(PlanningError):
            self.planner.create_plan("Do something random without a directory name")

    def test_full_execution_loop(self):
        test_dir = "./workspace/test_runtime_directory"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        goal = "Create a directory called test_runtime_directory"
        task = AgentTask(id="test-task-1", user_request=goal)

        plan = self.planner.create_plan(goal)
        result_task = self.controller.run_plan(task, plan)

        self.assertEqual(result_task.status, TaskStatus.COMPLETED)
        self.assertEqual(len(result_task.steps), 1)
        self.assertEqual(result_task.steps[0].status, StepStatus.SUCCESS)
        self.assertTrue(os.path.exists(test_dir))

        # Check events fired
        event_types = [e.event_type for e in self.events]
        self.assertIn(EventType.TASK_STARTED, event_types)
        self.assertIn(EventType.STEP_STARTED, event_types)
        self.assertIn(EventType.STEP_EXECUTED, event_types)
        self.assertIn(EventType.STEP_OBSERVED, event_types)
        self.assertIn(EventType.STEP_VERIFIED, event_types)
        self.assertIn(EventType.STEP_COMPLETED, event_types)
        self.assertIn(EventType.TASK_COMPLETED, event_types)

        # Clean up created directory
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
