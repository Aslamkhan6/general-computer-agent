"""
Security Gate & Human Approval View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QGroupBox, QPushButton, QHeaderView
    )
    from PySide6.QtCore import Signal, Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class SecurityView(QWidget):
        """View displaying Module 8 Security Gate, Pending Human Approvals, and Audit Logs."""

        approval_responded = Signal(str, bool)  # request_id, approved

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel("SECURITY GATE & HUMAN APPROVAL CENTER (MOD 8)", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            # Pending Approvals Group
            app_box = QGroupBox("PENDING HUMAN AUTHORIZATION REQUESTS", self)
            a_layout = QVBoxLayout(app_box)

            self.app_table = QTableWidget(0, 5, app_box)
            self.app_table.setHorizontalHeaderLabels(["Req ID", "Action / Tool", "Target Path", "Risk Level", "Actions"])
            self.app_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            a_layout.addWidget(self.app_table)

            layout.addWidget(app_box)

            # Audit Log Group
            audit_box = QGroupBox("SECURITY AUDIT TRAIL LOG", self)
            au_layout = QVBoxLayout(audit_box)

            self.audit_table = QTableWidget(0, 5, audit_box)
            self.audit_table.setHorizontalHeaderLabels(["Timestamp", "Agent Role", "Tool Name", "Risk Level", "Outcome"])
            self.audit_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            au_layout.addWidget(self.audit_table)

            layout.addWidget(audit_box)

        def set_pending_approvals(self, pending_list: list):
            """Populate pending approval prompts."""
            self.app_table.setRowCount(len(pending_list))
            for i, p in enumerate(pending_list):
                req_id = str(p.get("request_id", ""))
                self.app_table.setItem(i, 0, QTableWidgetItem(req_id))
                self.app_table.setItem(i, 1, QTableWidgetItem(str(p.get("tool_name", ""))))
                self.app_table.setItem(i, 2, QTableWidgetItem(str(p.get("target_resource", ""))))
                
                risk_item = QTableWidgetItem(str(p.get("risk_level", "")))
                risk_item.setForeground(Qt.yellow)
                self.app_table.setItem(i, 3, risk_item)

                # Approve / Deny button container
                btn_widget = QWidget()
                b_layout = QHBoxLayout(btn_widget)
                b_layout.setContentsMargins(2, 2, 2, 2)

                approve_btn = QPushButton("✓ Approve", btn_widget)
                approve_btn.setStyleSheet("background-color: #10b981; color: white; border-radius: 4px; padding: 2px 6px;")
                approve_btn.clicked.connect(lambda _, r=req_id: self.approval_responded.emit(r, True))

                deny_btn = QPushButton("✗ Deny", btn_widget)
                deny_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 4px; padding: 2px 6px;")
                deny_btn.clicked.connect(lambda _, r=req_id: self.approval_responded.emit(r, False))

                b_layout.addWidget(approve_btn)
                b_layout.addWidget(deny_btn)
                self.app_table.setCellWidget(i, 4, btn_widget)

        def set_audit_logs(self, audit_logs: list):
            """Populate security audit trail."""
            self.audit_table.setRowCount(len(audit_logs))
            for i, log in enumerate(audit_logs):
                self.audit_table.setItem(i, 0, QTableWidgetItem(str(log.get("timestamp", ""))))
                self.audit_table.setItem(i, 1, QTableWidgetItem(str(log.get("agent_role", ""))))
                self.audit_table.setItem(i, 2, QTableWidgetItem(str(log.get("tool_name", ""))))
                self.audit_table.setItem(i, 3, QTableWidgetItem(str(log.get("risk_level", ""))))
                self.audit_table.setItem(i, 4, QTableWidgetItem(str(log.get("outcome", ""))))

else:
    class SecurityView:
        """Headless fallback for SecurityView."""
        def __init__(self, parent=None):
            pass
        def set_pending_approvals(self, pending_list: list):
            pass
        def set_audit_logs(self, audit_logs: list):
            pass
