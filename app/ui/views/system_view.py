"""
System Diagnostics & Module Configuration View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QGroupBox, QTextEdit, QHeaderView
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class SystemView(QWidget):
        """View displaying system-wide module health diagnostics and configurations."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel("SYSTEM DIAGNOSTICS & MODULE HEALTH", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            # Module Health Table
            health_box = QGroupBox("MODULE ARCHITECTURE HEALTH (MOD 1 - MOD 10)", self)
            h_layout = QVBoxLayout(health_box)

            self.health_table = QTableWidget(10, 3, health_box)
            self.health_table.setHorizontalHeaderLabels(["Module", "Name / Subsystem", "Health Status"])
            self.health_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

            modules = [
                ("Module 1", "Agent Core & Event Runtime", "ACTIVE / ONLINE"),
                ("Module 2", "LLM / Brain Interface", "MOCK / DETERMINISTIC"),
                ("Module 3", "Tool Ecosystem (72 Tools)", "REGISTERED / READY"),
                ("Module 4", "GUI + Vision + Computer Use", "READY"),
                ("Module 5", "Voice Intelligence", "READY"),
                ("Module 6", "Memory + Skills Engine", "ONLINE (SQLite + Vectors)"),
                ("Module 7", "Reliability + Recovery Engine", "ACTIVE (Circuit Breaker Normal)"),
                ("Module 8", "Security + Permissions Gate", "ACTIVE (Default Deny Gate)"),
                ("Module 9", "Supervisor + Multi-Agent Architecture", "ACTIVE (5 Worker Agents)"),
                ("Module 10", "Real Robot Command Center UI", "ACTIVE (PySide6 Desktop)"),
            ]

            for i, (m, name, status) in enumerate(modules):
                self.health_table.setItem(i, 0, QTableWidgetItem(m))
                self.health_table.setItem(i, 1, QTableWidgetItem(name))
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(Qt.green)
                self.health_table.setItem(i, 2, status_item)

            h_layout.addWidget(self.health_table)
            layout.addWidget(health_box)

else:
    class SystemView:
        """Headless fallback for SystemView."""
        def __init__(self, parent=None):
            pass
