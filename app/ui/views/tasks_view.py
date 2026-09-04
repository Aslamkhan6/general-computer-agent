"""
Tasks & Workflow Management View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QPushButton, QGroupBox, QHeaderView
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class TasksView(QWidget):
        """View displaying active multi-agent task hierarchy and subtask status."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            # Header
            header = QLabel("TASK DISPATCHER & SUBTASK EXECUTION GRAPH", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            # Task Table
            self.task_table = QTableWidget(0, 5, self)
            self.task_table.setHorizontalHeaderLabels(["Task ID", "Goal / Subtask", "Assigned Worker", "Status", "Verified"])
            self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            layout.addWidget(self.task_table)

            # Controls
            btn_layout = QHBoxLayout()
            self.refresh_btn = QPushButton("🔄 Refresh Tasks", self)
            self.pause_btn = QPushButton("⏸️ Pause Dispatcher", self)
            self.clear_btn = QPushButton("🗑️ Clear History", self)
            
            btn_layout.addWidget(self.refresh_btn)
            btn_layout.addWidget(self.pause_btn)
            btn_layout.addWidget(self.clear_btn)
            btn_layout.addStretch()

            layout.addLayout(btn_layout)

        def set_tasks(self, task_list: list):
            """Populate task hierarchy table."""
            self.task_table.setRowCount(len(task_list))
            for i, item in enumerate(task_list):
                self.task_table.setItem(i, 0, QTableWidgetItem(str(item.get("task_id", ""))))
                self.task_table.setItem(i, 1, QTableWidgetItem(str(item.get("goal", ""))))
                self.task_table.setItem(i, 2, QTableWidgetItem(str(item.get("assigned_agent", ""))))
                self.task_table.setItem(i, 3, QTableWidgetItem(str(item.get("status", ""))))
                self.task_table.setItem(i, 4, QTableWidgetItem(str(item.get("verified", False))))

else:
    class TasksView:
        """Headless fallback for TasksView."""
        def __init__(self, parent=None):
            pass
        def set_tasks(self, task_list: list):
            pass
