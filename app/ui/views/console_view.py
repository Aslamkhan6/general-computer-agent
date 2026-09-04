"""
Main Console Overview View for Nexus Agent Command Center.
"""

from app.ui.robot_widget import RobotBrainWidget
from app.ui.models import RobotState, UIState

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
        QTextEdit, QPushButton, QGroupBox, QSplitter
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class ConsoleView(QWidget):
        """Primary console view containing Robot Brain canvas and event stream."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            # Main Vertical Splitter (Robot Canvas Top, Log Stream Bottom)
            splitter = QSplitter(Qt.Vertical, self)

            # Top Container: Robot Brain + Task Info
            top_widget = QWidget(self)
            top_layout = QVBoxLayout(top_widget)
            top_layout.setContentsMargins(0, 0, 0, 0)

            # Task Header Box
            task_box = QGroupBox("ACTIVE TASK EXECUTION", top_widget)
            tb_layout = QVBoxLayout(task_box)

            self.task_goal_label = QLabel("Goal: System Standby (Waiting for user prompt)", task_box)
            self.task_goal_label.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 13px;")
            tb_layout.addWidget(self.task_goal_label)

            self.task_progress = QProgressBar(task_box)
            self.task_progress.setValue(0)
            tb_layout.addWidget(self.task_progress)

            top_layout.addWidget(task_box)

            # Robot Brain Canvas
            self.robot_canvas = RobotBrainWidget(top_widget)
            top_layout.addWidget(self.robot_canvas, stretch=1)

            splitter.addWidget(top_widget)

            # Bottom Container: Real-Time Event Log Stream
            log_box = QGroupBox("LIVE EVENT LOG STREAM", self)
            lb_layout = QVBoxLayout(log_box)

            self.log_output = QTextEdit(log_box)
            self.log_output.setReadOnly(True)
            self.log_output.setStyleSheet("font-family: monospace; font-size: 11px; background-color: #090d15;")
            lb_layout.addWidget(self.log_output)

            splitter.addWidget(log_box)
            splitter.setSizes([350, 200])

            layout.addWidget(splitter)

            # Initial welcome log
            self.append_log("INFO", "Nexus Agent Command Console Initialized.")
            self.append_log("INFO", "Modules 1-9 Active: Core, Memory, Tools, Vision, Voice, Security, Recovery, Supervisor.")

        def update_state(self, ui_state: UIState):
            """Update labels and canvas from UI state model."""
            self.task_goal_label.setText(f"Goal: {ui_state.active_task_goal}")
            self.task_progress.setValue(int(ui_state.task_progress))
            self.robot_canvas.set_state(
                ui_state.robot_state,
                active_tool=ui_state.active_tool_name or "Idle",
                active_agent=ui_state.active_agent_role or "Supervisor"
            )

        def append_log(self, level: str, message: str):
            """Append formatted line to event log stream."""
            color = "#00f0ff" if level == "INFO" else "#ffaa00" if level == "WARN" else "#ff3366"
            html_line = f'<span style="color: #6b7280;">[SYSTEM]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> {message}'
            self.log_output.append(html_line)

else:
    class ConsoleView:
        """Headless fallback for ConsoleView."""
        def __init__(self, parent=None):
            pass
        def update_state(self, ui_state: UIState):
            pass
        def append_log(self, level: str, message: str):
            pass
