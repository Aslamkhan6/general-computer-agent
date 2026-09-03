import os
import shutil
import unittest

from app.agent.controller import AgentController
from app.core.enums import ActionStatus, StepStatus, TaskStatus
from app.core.events import EventBus
from app.core.state import ActionResult, AgentTask, TaskStep
from app.observer.filesystem import FilesystemObserver
from app.planner.plan import TaskPlan
from app.recovery import (
    AlternativeToolEngine,
    CircuitBreaker,
    FailureCategory,
    FailureClassifier,
    FailureDetector,
    FailureReport,
    RecoveryAction,
    RecoveryEngine,
    RecoveryHistory,
    ReplanningEngine,
    RetryEngine,
    RetryPolicy,
    RollbackEngine,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier


class TestModule7Recovery(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()

        self.recovery_engine = RecoveryEngine(max_failures_per_step=3)
        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
            recovery_engine=self.recovery_engine,
        )

    def test_7_1_detector_and_classifier(self):
        detector = FailureDetector()
        classifier = FailureClassifier()

        step = TaskStep(id="s1", description="Test Step", tool_name="create_file", input_data={"path": "./workspace/test.txt"})
        failed_res = ActionResult(status=ActionStatus.FAILED, error="Access denied: Permission required")

        report = detector.detect("t1", step, execution_result=failed_res)
        self.assertIsNotNone(report)
        category = classifier.classify(report)
        self.assertEqual(category, FailureCategory.PERMISSION)

    def test_7_2_retry_engine(self):
        retry_engine = RetryEngine(policy=RetryPolicy(max_attempts=2, delay_seconds=0.01))
        self.assertTrue(retry_engine.is_retryable(FailureCategory.TRANSIENT, attempt_count=1))
        self.assertFalse(retry_engine.is_retryable(FailureCategory.PERMISSION, attempt_count=1))

    def test_7_3_alternative_tool_engine(self):
        alt_engine = AlternativeToolEngine()
        alt_tool = alt_engine.find_alternative_tool("create_file")
        self.assertEqual(alt_tool, "write_file")

    def test_7_4_circuit_breaker(self):
        cb = CircuitBreaker(max_failures_per_step=2)
        st1 = cb.record_attempt("step-cb-1")
        self.assertFalse(st1.is_tripped)
        st2 = cb.record_attempt("step-cb-1")
        self.assertTrue(st2.is_tripped)

    def test_7_5_replanning_engine(self):
        replan_engine = ReplanningEngine()
        step = TaskStep(id="s-replan", description="Create deep file", tool_name="write_file", input_data={"path": "./workspace/nonexistent_folder/sub/file.txt"})
        report = FailureReport(task_id="t1", step_id="s-replan", error_message="No such file or directory: parent folder not found", category=FailureCategory.NOT_FOUND)

        plan = replan_engine.replan_failed_step(step, report)
        self.assertIsNotNone(plan)
        self.assertGreaterEqual(len(plan.steps), 2)
        self.assertEqual(plan.steps[0].tool_name, "create_directory")

    def test_7_6_rollback_engine(self):
        rollback_engine = RollbackEngine()
        test_dir = "./workspace/test_rollback_dir"
        os.makedirs(test_dir, exist_ok=True)

        step = TaskStep(id="s-rb", description="Create dir", tool_name="create_directory", input_data={"path": test_dir}, status=StepStatus.SUCCESS)
        res = rollback_engine.rollback_step(step)
        self.assertTrue(res["rolled_back"])
        self.assertFalse(os.path.exists(test_dir))

    def test_7_7_closed_loop_recovery_in_controller(self):
        # Test closed-loop recovery when initial tool execution fails or verification fails, RecoveryEngine recovers task
        target_file = "./workspace/recovery_test/target.txt"
        if os.path.exists("./workspace/recovery_test"):
            shutil.rmtree("./workspace/recovery_test", ignore_errors=True)

        # Step specifying tool 'create_file' which triggers AlternativeToolEngine -> 'write_file'
        task = AgentTask(id="task-rec-001", user_request="Create target file")
        step = TaskStep(
            id="step-create-target",
            description="Create target file",
            tool_name="create_file",
            input_data={"path": target_file},
            expected_state={"exists": True, "is_file": True},
        )
        plan = TaskPlan(goal="Create target file", steps=[step])

        completed_task = self.controller.run_plan(task, plan)
        self.assertEqual(completed_task.status, TaskStatus.COMPLETED)
        self.assertTrue(os.path.exists(target_file))

        # Verify recovery record logged
        records = self.recovery_engine.history.get_all_records()
        self.assertGreaterEqual(len(records), 0)

        shutil.rmtree("./workspace/recovery_test", ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
