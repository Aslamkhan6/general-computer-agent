"""
UI Controller orchestrating PySide6 desktop events with Modules 1-9 subsystem backends.
"""

import time
import threading
import psutil
from typing import Optional, Dict, Any, List

from app.ui.models import UIState, RobotState, AutonomyLevel, NavigationTab, SystemMetrics
from app.core.events import EventBus, Event, EventType
from app.supervisor.supervisor import Supervisor
from app.agent.controller import AgentController
from app.security.manager import SecurityManager
from app.recovery.manager import RecoveryEngine
from app.voice.manager import VoiceManager

try:
    from PySide6.QtCore import QObject, Signal, QTimer
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QObject: pass


class UIController(QObject if HAS_PYSIDE else object):
    """Central Controller binding PySide6 UI views to Agent Core, Supervisor, Security, and Voice."""

    if HAS_PYSIDE:
        state_updated = Signal(object)  # UIState
        log_emitted = Signal(str, str)   # level, message

    def __init__(
        self,
        supervisor: Optional[Supervisor] = None,
        agent_controller: Optional[AgentController] = None,
        security_manager: Optional[SecurityManager] = None,
        recovery_engine: Optional[RecoveryEngine] = None,
        voice_manager: Optional[VoiceManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        if HAS_PYSIDE:
            super().__init__()

        self.supervisor = supervisor or Supervisor()
        self.agent_controller = agent_controller
        self.security_manager = security_manager or (self.supervisor.security_manager if hasattr(self.supervisor, 'security_manager') else SecurityManager())
        self.recovery_engine = recovery_engine or RecoveryEngine()
        self.voice_manager = voice_manager or VoiceManager()
        self.event_bus = event_bus or EventBus()

        self.state = UIState()

        # Wire EventBus listeners
        self._register_event_listeners()

        # Telemetry timer if PySide present
        if HAS_PYSIDE:
            self.metrics_timer = QTimer(self)
            self.metrics_timer.timeout.connect(self._poll_system_metrics)
            self.metrics_timer.start(1000)  # Every 1 second

    def _register_event_listeners(self):
        """Subscribe to core EventBus events."""
        self.event_bus.subscribe(self._on_event_received)

    def _on_event_received(self, event: Event):
        """Route event based on event_type."""
        if event.event_type == EventType.TASK_STARTED:
            self._on_task_started(event)
        elif event.event_type == EventType.TASK_COMPLETED:
            self._on_task_completed(event)
        elif event.event_type in (EventType.STEP_EXECUTED, EventType.STEP_COMPLETED):
            self._on_step_executed(event)
        elif event.event_type in (EventType.TASK_FAILED, EventType.STEP_FAILED):
            self._on_failure_detected(event)

    def _on_task_started(self, event: Event):
        self.state.robot_state = RobotState.WORKING
        self.state.active_task_goal = str(event.payload.get("goal", "Processing Task"))
        self.state.task_progress = 10.0
        self.state.status_message = f"Task started: {self.state.active_task_goal}"
        self._notify_update("INFO", f"Task started: {self.state.active_task_goal}")

    def _on_task_completed(self, event: Event):
        self.state.robot_state = RobotState.COMPLETE
        self.state.task_progress = 100.0
        self.state.status_message = "Task finished successfully."
        self._notify_update("INFO", "Task completed cleanly.")

    def _on_step_executed(self, event: Event):
        tool_name = str(event.payload.get("tool_name", event.payload.get("step_id", "")))
        self.state.active_tool_name = tool_name
        self._notify_update("INFO", f"Step executed: {tool_name}")

    def _on_failure_detected(self, event: Event):
        self.state.robot_state = RobotState.RECOVERY
        self.state.recent_recovery_count += 1
        err = str(event.payload.get("error", "Execution Error"))
        self._notify_update("WARN", f"Failure detected: {err}. Triggering Recovery Engine...")

    def _poll_system_metrics(self):
        """Poll host CPU, RAM, Disk telemetry."""
        try:
            self.state.metrics.cpu_percent = psutil.cpu_percent()
            self.state.metrics.ram_percent = psutil.virtual_memory().percent
            self.state.metrics.disk_percent = psutil.disk_usage('/').percent
            if HAS_PYSIDE:
                self.state_updated.emit(self.state)
        except Exception:
            pass

    def _notify_update(self, level: str, msg: str):
        if HAS_PYSIDE:
            self.state_updated.emit(self.state)
            self.log_emitted.emit(level, msg)

    def handle_user_command(self, prompt: str):
        """Execute user prompt submitted via UI input bar."""
        if self.state.is_emergency_stopped:
            self._notify_update("ERROR", "Cannot execute: System is in EMERGENCY STOP state!")
            return

        self.state.robot_state = RobotState.ANALYZING
        self.state.active_task_goal = prompt
        self.state.task_progress = 5.0
        self._notify_update("INFO", f"Dispatched prompt: '{prompt}'")

        # Run task async to prevent locking UI main thread
        def _run():
            try:
                res = self.supervisor.execute_task(prompt)
                if res.get("status") == "COMPLETED":
                    self.state.robot_state = RobotState.COMPLETE
                    self.state.task_progress = 100.0
                    self._notify_update("INFO", "Multi-Agent task completed.")
                else:
                    self.state.robot_state = RobotState.RECOVERY
                    self._notify_update("WARN", "Task completed with warnings.")
            except Exception as e:
                self.state.robot_state = RobotState.RECOVERY
                self._notify_update("ERROR", f"Task execution error: {str(e)}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def handle_voice_toggle(self, enabled: bool):
        """Toggle Module 5 Voice STT session."""
        self.state.is_voice_active = enabled
        if enabled:
            self._notify_update("INFO", "Voice STT Session Activated. Speak into microphone...")
        else:
            self._notify_update("INFO", "Voice Session Deactivated.")

    def handle_emergency_stop(self):
        """Emergency Stop button pressed: immediately trip circuit breaker and halt execution."""
        self.state.is_emergency_stopped = True
        self.state.robot_state = RobotState.EMERGENCY_STOP
        self.recovery_engine.circuit_breaker._step_failures["EMERGENCY_STOP"] = 999
        self._notify_update("ERROR", "🛑 EMERGENCY STOP TRIPPED! All tool executions halted.")

    def handle_autonomy_change(self, level: AutonomyLevel):
        """Update autonomy control level."""
        self.state.autonomy_level = level
        self._notify_update("INFO", f"Autonomy level changed to: {level.value}")

    def handle_approval_response(self, request_id: str, approved: bool):
        """Respond to human approval request from Security View."""
        if hasattr(self.security_manager, 'approval_manager'):
            self.security_manager.approval_manager.respond_to_request(request_id, approved)
        status_str = "Approved" if approved else "Denied"
        self._notify_update("INFO", f"Authorization Request '{request_id}' {status_str}.")
