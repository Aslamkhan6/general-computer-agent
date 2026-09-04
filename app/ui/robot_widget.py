"""
Robot Brain Visualization Widget for Nexus Agent Command Center.
"""

import math
from typing import Optional
from app.ui.models import RobotState

try:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass  # Fallback stub for headless environment


if HAS_PYSIDE:
    class RobotBrainWidget(QWidget):
        """Interactive visualizer for the Robot Brain state and multi-agent network."""

        STATE_COLORS = {
            RobotState.STANDBY: QColor(0, 119, 255),       # Blue
            RobotState.ANALYZING: QColor(255, 170, 0),     # Gold/Amber
            RobotState.WORKING: QColor(0, 240, 255),       # Neon Cyan
            RobotState.VERIFYING: QColor(168, 85, 247),    # Purple
            RobotState.RECOVERY: QColor(255, 107, 0),      # Orange
            RobotState.APPROVAL: QColor(245, 158, 11),     # Amber Alert
            RobotState.COMPLETE: QColor(16, 185, 129),     # Emerald Green
            RobotState.EMERGENCY_STOP: QColor(239, 68, 68),# Red
        }

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("RobotCanvas")
            self.setMinimumSize(400, 320)

            self.robot_state = RobotState.STANDBY
            self.pulse_phase = 0.0
            self.angle_offset = 0.0
            self.active_tool = "Idle"
            self.active_agent = "Supervisor"

            # Animation timer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._on_animate)
            self.timer.start(33)  # ~30 FPS

        def set_state(self, state: RobotState, active_tool: str = "", active_agent: str = ""):
            """Update state and force repaint."""
            self.robot_state = state
            if active_tool:
                self.active_tool = active_tool
            if active_agent:
                self.active_agent = active_agent
            self.update()

        def _on_animate(self):
            """Advance animation pulse and rotation."""
            self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)
            self.angle_offset = (self.angle_offset + 0.02) % (2 * math.pi)
            self.update()

        def paintEvent(self, event):
            """Custom QPainter rendering of Robot Brain core & orbitals."""
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w, h = self.width(), self.height()
            center_x, center_y = w / 2.0, h / 2.0
            color = self.STATE_COLORS.get(self.robot_state, QColor(0, 240, 255))

            # 1. Background Grid Subtle Lines
            painter.setPen(QPen(QColor(25, 35, 55), 1, Qt.DashLine))
            painter.drawLine(0, int(center_y), w, int(center_y))
            painter.drawLine(int(center_x), 0, int(center_x), h)

            # 2. Outer Orbital Ring
            orbit_radius = min(w, h) * 0.35
            painter.setPen(QPen(QColor(30, 45, 70), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), orbit_radius, orbit_radius)

            # 3. Worker Agent Nodes orbiting around Brain Core
            agents = ["Research", "Coding", "Computer", "Browser", "Verification"]
            num_agents = len(agents)
            for i, agent_name in enumerate(agents):
                angle = self.angle_offset + (i * 2 * math.pi / num_agents)
                node_x = center_x + orbit_radius * math.cos(angle)
                node_y = center_y + orbit_radius * math.sin(angle)

                # Connecting beam to center core
                painter.setPen(QPen(QColor(0, 240, 255, 60), 1, Qt.DotLine))
                painter.drawLine(QPointF(center_x, center_y), QPointF(node_x, node_y))

                # Agent Node Circle
                painter.setPen(QPen(QColor(0, 240, 255), 1.5))
                painter.setBrush(QBrush(QColor(13, 20, 32)))
                painter.drawEllipse(QPointF(node_x, node_y), 12, 12)

                # Node Label
                painter.setFont(QFont("Segoe UI", 8))
                painter.setPen(QColor(160, 180, 205))
                painter.drawText(int(node_x - 30), int(node_y + 24), 60, 15, Qt.AlignCenter, agent_name)

            # 4. Pulsing Brain Core Glow
            pulse_scale = 1.0 + 0.08 * math.sin(self.pulse_phase)
            core_radius = min(w, h) * 0.18 * pulse_scale

            gradient = QRadialGradient(QPointF(center_x, center_y), core_radius * 1.6)
            gradient.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), 200))
            gradient.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 80))
            gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPointF(center_x, center_y), core_radius * 1.6, core_radius * 1.6)

            # Inner Core Circle
            painter.setPen(QPen(color.lighter(130), 3))
            painter.setBrush(QBrush(QColor(10, 15, 25)))
            painter.drawEllipse(QPointF(center_x, center_y), core_radius, core_radius)

            # 5. Core Text Details
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.setPen(color)
            painter.drawText(int(center_x - 80), int(center_y - 12), 160, 25, Qt.AlignCenter, self.robot_state.value)

            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor(200, 220, 245))
            painter.drawText(int(center_x - 100), int(center_y + 12), 200, 20, Qt.AlignCenter, f"Tool: {self.active_tool}")

            painter.end()

else:
    class RobotBrainWidget:
        """Headless fallback for RobotBrainWidget."""
        def __init__(self, parent=None):
            self.robot_state = RobotState.STANDBY
            self.active_tool = "Idle"
            self.active_agent = "Supervisor"

        def set_state(self, state: RobotState, active_tool: str = "", active_agent: str = ""):
            self.robot_state = state
            if active_tool:
                self.active_tool = active_tool
            if active_agent:
                self.active_agent = active_agent
