"""
Right Diagnostic & System Monitor Widget for Nexus Agent Command Center.
"""

from app.ui.models import AutonomyLevel, SystemMetrics

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QProgressBar, QGroupBox,
        QRadioButton, QButtonGroup, QHBoxLayout
    )
    from PySide6.QtCore import Signal
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class SystemMonitorWidget(QWidget):
        """Right diagnostic sidebar for real-time telemetry and autonomy control."""

        autonomy_changed = Signal(AutonomyLevel)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("MonitorWidget")
            self.setFixedWidth(240)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(12)

            # Title
            title = QLabel("SYSTEM MONITOR", self)
            title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(title)

            # 1. Telemetry Metrics Group
            telemetry_group = QGroupBox("HOST RESOURCES", self)
            t_layout = QVBoxLayout(telemetry_group)

            t_layout.addWidget(QLabel("CPU Usage:", self))
            self.cpu_bar = QProgressBar(self)
            self.cpu_bar.setRange(0, 100)
            t_layout.addWidget(self.cpu_bar)

            t_layout.addWidget(QLabel("RAM Usage:", self))
            self.ram_bar = QProgressBar(self)
            self.ram_bar.setRange(0, 100)
            t_layout.addWidget(self.ram_bar)

            t_layout.addWidget(QLabel("Disk Space:", self))
            self.disk_bar = QProgressBar(self)
            self.disk_bar.setRange(0, 100)
            t_layout.addWidget(self.disk_bar)

            self.net_label = QLabel("Network: 0.0 KB/s", self)
            self.net_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
            t_layout.addWidget(self.net_label)

            layout.addWidget(telemetry_group)

            # 2. Security Subsystem Group
            sec_group = QGroupBox("SECURITY GATE (MOD 8)", self)
            sec_layout = QVBoxLayout(sec_group)
            self.sec_gate_label = QLabel("Policy Gate: DEFAULT DENY", self)
            self.sec_gate_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 11px;")
            sec_layout.addWidget(self.sec_gate_label)

            self.sec_sanitizer_label = QLabel("Secret Sanitizer: ACTIVE", self)
            self.sec_sanitizer_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
            sec_layout.addWidget(self.sec_sanitizer_label)

            self.pending_approvals_label = QLabel("Pending Approvals: 0", self)
            self.pending_approvals_label.setStyleSheet("color: #f59e0b; font-size: 11px;")
            sec_layout.addWidget(self.pending_approvals_label)

            layout.addWidget(sec_group)

            # 3. Recovery Subsystem Group
            rec_group = QGroupBox("RECOVERY ENGINE (MOD 7)", self)
            rec_layout = QVBoxLayout(rec_group)
            self.cb_status_label = QLabel("Circuit Breaker: CLOSED (NORMAL)", self)
            self.cb_status_label.setStyleSheet("color: #00ff88; font-size: 11px;")
            rec_layout.addWidget(self.cb_status_label)

            self.recovery_count_label = QLabel("Recovery Actions: 0", self)
            self.recovery_count_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
            rec_layout.addWidget(self.recovery_count_label)

            layout.addWidget(rec_group)

            # 4. Autonomy Level Control Group
            autonomy_group = QGroupBox("AUTONOMY LEVEL", self)
            a_layout = QVBoxLayout(autonomy_group)

            self.autonomy_bg = QButtonGroup(self)
            
            self.radio_autonomous = QRadioButton("Level 3: Autonomous", self)
            self.radio_assisted = QRadioButton("Level 2: Assisted (Rec)", self)
            self.radio_manual = QRadioButton("Level 1: Manual Step", self)

            self.radio_assisted.setChecked(True)

            self.autonomy_bg.addButton(self.radio_autonomous, 3)
            self.autonomy_bg.addButton(self.radio_assisted, 2)
            self.autonomy_bg.addButton(self.radio_manual, 1)

            a_layout.addWidget(self.radio_autonomous)
            a_layout.addWidget(self.radio_assisted)
            a_layout.addWidget(self.radio_manual)

            self.autonomy_bg.idClicked.connect(self._on_autonomy_selected)

            layout.addWidget(autonomy_group)

            layout.addStretch()

        def _on_autonomy_selected(self, id_val: int):
            if id_val == 3:
                self.autonomy_changed.emit(AutonomyLevel.AUTONOMOUS)
            elif id_val == 2:
                self.autonomy_changed.emit(AutonomyLevel.ASSISTED)
            else:
                self.autonomy_changed.emit(AutonomyLevel.MANUAL)

        def update_metrics(self, metrics: SystemMetrics):
            """Update system resource progress bars."""
            self.cpu_bar.setValue(int(metrics.cpu_percent))
            self.ram_bar.setValue(int(metrics.ram_percent))
            self.disk_bar.setValue(int(metrics.disk_percent))
            self.net_label.setText(f"Network: {metrics.network_kbps:.1f} KB/s")

        def update_security_status(self, pending_count: int):
            """Update security pending count."""
            self.pending_approvals_label.setText(f"Pending Approvals: {pending_count}")

        def update_recovery_status(self, recovery_count: int, is_tripped: bool = False):
            """Update recovery count and circuit breaker status."""
            self.recovery_count_label.setText(f"Recovery Actions: {recovery_count}")
            if is_tripped:
                self.cb_status_label.setText("Circuit Breaker: TRIPPED")
                self.cb_status_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px;")
            else:
                self.cb_status_label.setText("Circuit Breaker: CLOSED (NORMAL)")
                self.cb_status_label.setStyleSheet("color: #00ff88; font-size: 11px;")

else:
    class SystemMonitorWidget:
        """Headless fallback for SystemMonitorWidget."""
        def __init__(self, parent=None):
            self.autonomy_level = AutonomyLevel.ASSISTED
        def update_metrics(self, metrics: SystemMetrics):
            pass
        def update_security_status(self, pending_count: int):
            pass
        def update_recovery_status(self, recovery_count: int, is_tripped: bool = False):
            pass
