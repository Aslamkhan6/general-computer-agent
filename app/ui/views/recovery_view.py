"""
Recovery Engine & Failure Diagnostic View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QGroupBox, QPushButton, QHeaderView
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class RecoveryView(QWidget):
        """View displaying Module 7 Reliability & Failure Recovery Engine telemetry."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel("RELIABILITY & RECOVERY ENGINE (MOD 7)", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            # Failure Reports Table
            fail_box = QGroupBox("DETECTED FAILURES & RECOVERY ACTIONS", self)
            f_layout = QVBoxLayout(fail_box)

            self.fail_table = QTableWidget(0, 5, fail_box)
            self.fail_table.setHorizontalHeaderLabels(["Task ID", "Failure Category", "Action Taken", "Attempts", "Success"])
            self.fail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            f_layout.addWidget(self.fail_table)

            layout.addWidget(fail_box)

            # Controls
            btn_layout = QHBoxLayout()
            self.reset_cb_btn = QPushButton("⚡ Reset Circuit Breakers", self)
            self.rollback_btn = QPushButton("↩️ Trigger Rollback", self)
            
            btn_layout.addWidget(self.reset_cb_btn)
            btn_layout.addWidget(self.rollback_btn)
            btn_layout.addStretch()

            layout.addLayout(btn_layout)

        def set_recovery_records(self, records: list):
            """Populate recovery records table."""
            self.fail_table.setRowCount(len(records))
            for i, r in enumerate(records):
                self.fail_table.setItem(i, 0, QTableWidgetItem(str(r.get("task_id", ""))))
                self.fail_table.setItem(i, 1, QTableWidgetItem(str(r.get("category", ""))))
                self.fail_table.setItem(i, 2, QTableWidgetItem(str(r.get("action", ""))))
                self.fail_table.setItem(i, 3, QTableWidgetItem(str(r.get("attempts", 1))))
                
                success_item = QTableWidgetItem(str(r.get("success", True)))
                if r.get("success", True):
                    success_item.setForeground(Qt.green)
                else:
                    success_item.setForeground(Qt.red)
                self.fail_table.setItem(i, 4, success_item)

else:
    class RecoveryView:
        """Headless fallback for RecoveryView."""
        def __init__(self, parent=None):
            pass
        def set_recovery_records(self, records: list):
            pass
