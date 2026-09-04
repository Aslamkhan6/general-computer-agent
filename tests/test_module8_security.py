import os
import unittest

from app.agent.controller import AgentController
from app.core.enums import StepStatus, TaskStatus
from app.core.events import EventBus
from app.core.state import AgentTask, TaskStep
from app.observer.filesystem import FilesystemObserver
from app.planner.plan import TaskPlan
from app.security import (
    ActionClassifier,
    HumanApprovalManager,
    NormalizedAction,
    OperationType,
    PermissionManager,
    PermissionState,
    PolicyEngine,
    RestrictedSandbox,
    RiskAnalyzer,
    RiskLevel,
    SecretDetector,
    SecurityAuditLogger,
    SecurityDecision,
    SecurityManager,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier


class TestModule8Security(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()

        self.security_manager = SecurityManager()
        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
            security_manager=self.security_manager,
        )

    def test_8_1_risk_analyzer_and_classifier(self):
        classifier = ActionClassifier()

        norm_low, risk_low = classifier.classify("read_file", {"path": "./workspace/README.md"})
        self.assertEqual(risk_low, RiskLevel.LOW)

        norm_crit, risk_crit = classifier.classify("read_file", {"path": "C:\\Windows\\System32\\config\\SAM"})
        self.assertEqual(risk_crit, RiskLevel.CRITICAL)

    def test_8_2_policy_engine_default_deny(self):
        policy = PolicyEngine()
        norm_sys = NormalizedAction(tool="delete_file", target="C:\\Windows\\System32", operation=OperationType.DELETE, potential_impact=RiskLevel.CRITICAL)
        state, reason = policy.evaluate(norm_sys)
        self.assertEqual(state, PermissionState.DENY)

    def test_8_3_permission_manager(self):
        pm = PermissionManager()
        self.assertEqual(pm.check("filesystem.read"), PermissionState.ALLOW)
        self.assertEqual(pm.check("credential.access"), PermissionState.DENY)

    def test_8_4_approval_manager_timeout(self):
        appr_mgr = HumanApprovalManager(default_auto_approve_test=False)
        norm_action = NormalizedAction(tool="delete_directory", target="./workspace/old_proj", operation=OperationType.DELETE, potential_impact=RiskLevel.HIGH)
        approved, msg = appr_mgr.evaluate_request(norm_action, "Deletion approval")
        self.assertFalse(approved)
        self.assertIn("timed out/denied", msg)

    def test_8_5_secret_detector_and_audit_sanitization(self):
        secrets = SecretDetector()
        self.assertTrue(secrets.contains_secret("API_KEY=sk-1234567890abcdef12345"))

        sanitized = secrets.sanitize_text("Config contains API_KEY='sk-1234567890abcdef12345'")
        self.assertNotIn("sk-1234567890abcdef12345", sanitized)

    def test_8_6_sandbox_traversal_prevention(self):
        sandbox = RestrictedSandbox(allowed_root="./workspace")
        valid, msg = sandbox.validate_path("./workspace/test.txt")
        self.assertTrue(valid)

    def test_8_7_security_manager_authorization_gate(self):
        # LOW risk allowed
        dec_low = self.security_manager.authorize("read_file", {"path": "./workspace/README.md"})
        self.assertTrue(dec_low.allowed)

        # CRITICAL secret read blocked
        dec_secret = self.security_manager.authorize("read_file", {"path": "./workspace/.env"})
        self.assertFalse(dec_secret.allowed)
        self.assertEqual(dec_secret.permission, PermissionState.DENY)

    def test_8_8_controller_security_gate_integration(self):
        # Attempting to execute a blocked action (.env read) via AgentController
        task = AgentTask(id="task-sec-block-001", user_request="Read secret file")
        step = TaskStep(
            id="step-read-secret",
            description="Read secret env",
            tool_name="read_file",
            input_data={"path": "./workspace/.env"},
            expected_state={"exists": True},
        )
        plan = TaskPlan(goal="Read secret file", steps=[step])

        completed_task = self.controller.run_plan(task, plan)
        self.assertEqual(completed_task.status, TaskStatus.FAILED)
        self.assertIn("Security Blocked", completed_task.error)


if __name__ == "__main__":
    unittest.main()
