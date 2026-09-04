"""
Unit tests for Module 10 — Real Robot Command Center (Nexus Agent UI).
"""

import unittest
from app.core.enums import ActionStatus
from app.ui.models import RobotState, AutonomyLevel, NavigationTab, UIState, SystemMetrics
from app.ui.controller import UIController
from app.tools.ui_tools import (
    GetUIStateTool, SendUINotificationTool, UpdateRobotStateTool, TriggerUIApprovalTool
)
from app.core.events import EventBus, Event, EventType
from app.recovery.manager import RecoveryEngine
from app.security.manager import SecurityManager


class TestModule10UI(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.recovery_engine = RecoveryEngine()
        self.security_manager = SecurityManager()

    def test_ui_models(self):
        state = UIState(
            robot_state=RobotState.WORKING,
            autonomy_level=AutonomyLevel.ASSISTED,
            active_tab=NavigationTab.CONSOLE,
            active_task_goal="Create VoiceTest folder",
            task_progress=50.0
        )
        self.assertEqual(state.robot_state, RobotState.WORKING)
        self.assertEqual(state.autonomy_level, AutonomyLevel.ASSISTED)
        self.assertEqual(state.active_tab, NavigationTab.CONSOLE)

        d = state.to_dict()
        self.assertEqual(d["robot_state"], "WORKING")
        self.assertEqual(d["task_progress"], 50.0)

    def test_ui_controller_events(self):
        controller = UIController(
            security_manager=self.security_manager,
            recovery_engine=self.recovery_engine,
            event_bus=self.event_bus
        )

        # Test EventBus subscription on TASK_STARTED
        event = Event(event_type=EventType.TASK_STARTED, task_id="task-101", payload={"goal": "Test Task Unit"})
        self.event_bus.publish(event)

        self.assertEqual(controller.state.robot_state, RobotState.WORKING)
        self.assertIn("Test Task Unit", controller.state.active_task_goal)

        # Test EventBus subscription on TASK_COMPLETED
        event_complete = Event(event_type=EventType.TASK_COMPLETED, task_id="task-101", payload={"result": "success"})
        self.event_bus.publish(event_complete)

        self.assertEqual(controller.state.robot_state, RobotState.COMPLETE)

    def test_emergency_stop_mechanic(self):
        controller = UIController(
            security_manager=self.security_manager,
            recovery_engine=self.recovery_engine,
            event_bus=self.event_bus
        )
        self.assertFalse(controller.state.is_emergency_stopped)
        self.assertFalse(self.recovery_engine.circuit_breaker.is_tripped("EMERGENCY_STOP"))

        controller.handle_emergency_stop()

        self.assertTrue(controller.state.is_emergency_stopped)
        self.assertEqual(controller.state.robot_state, RobotState.EMERGENCY_STOP)
        self.assertTrue(self.recovery_engine.circuit_breaker.is_tripped("EMERGENCY_STOP"))

    def test_autonomy_level_change(self):
        controller = UIController(
            security_manager=self.security_manager,
            recovery_engine=self.recovery_engine,
            event_bus=self.event_bus
        )
        controller.handle_autonomy_change(AutonomyLevel.AUTONOMOUS)
        self.assertEqual(controller.state.autonomy_level, AutonomyLevel.AUTONOMOUS)

    def test_ui_tools_execution(self):
        tool1 = GetUIStateTool()
        res1 = tool1.execute()
        self.assertEqual(res1.status, ActionStatus.SUCCESS)
        self.assertIn("robot_state", res1.output)

        tool2 = SendUINotificationTool()
        res2 = tool2.execute(message="Hello Console", level="INFO")
        self.assertEqual(res2.status, ActionStatus.SUCCESS)
        self.assertEqual(res2.output["message"], "Hello Console")

        tool3 = UpdateRobotStateTool()
        res3 = tool3.execute(state="VERIFYING", active_tool="test_tool")
        self.assertEqual(res3.status, ActionStatus.SUCCESS)
        self.assertEqual(res3.output["robot_state"], "VERIFYING")

        tool4 = TriggerUIApprovalTool()
        res4 = tool4.execute(request_id="req-101", action_summary="Delete files")
        self.assertEqual(res4.status, ActionStatus.SUCCESS)
        self.assertEqual(res4.output["request_id"], "req-101")


if __name__ == "__main__":
    unittest.main()
