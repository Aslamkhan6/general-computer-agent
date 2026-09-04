"""
Main PySide6 Window for Nexus Agent Desktop Command Center.
"""

from typing import Optional
from app.ui.models import NavigationTab, UIState, RobotState
from app.ui.theme import NEXUS_DARK_THEME
from app.ui.sidebar_widget import SidebarWidget
from app.ui.monitor_widget import SystemMonitorWidget
from app.ui.input_widget import CommandInputWidget
from app.ui.views.console_view import ConsoleView
from app.ui.views.tasks_view import TasksView
from app.ui.views.agents_view import AgentsView
from app.ui.views.computer_view import ComputerView
from app.ui.views.memory_view import MemoryView
from app.ui.views.security_view import SecurityView
from app.ui.views.recovery_view import RecoveryView
from app.ui.views.system_view import SystemView

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
        QSystemTrayIcon, QMenu, QApplication, QLabel
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QAction
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QMainWindow: pass


if HAS_PYSIDE:
    class NexusMainWindow(QMainWindow):
        """Native PySide6 Desktop Application Window for Nexus Agent."""

        def __init__(self, controller=None):
            super().__init__()
            self.controller = controller
            self.setWindowTitle("Nexus Agent — Real Robot Command Center")
            self.resize(1280, 800)
            self.setMinimumSize(1024, 640)

            # Apply QSS Dark Theme
            self.setStyleSheet(NEXUS_DARK_THEME)

            # Central Widget & Layout
            central = QWidget(self)
            self.setCentralWidget(central)
            main_v_layout = QVBoxLayout(central)
            main_v_layout.setContentsMargins(0, 0, 0, 0)
            main_v_layout.setSpacing(0)

            # Middle Container (Sidebar + Stacked Views + Monitor)
            mid_widget = QWidget(self)
            mid_h_layout = QHBoxLayout(mid_widget)
            mid_h_layout.setContentsMargins(0, 0, 0, 0)
            mid_h_layout.setSpacing(0)

            # Left Navigation Sidebar
            self.sidebar = SidebarWidget(mid_widget)
            self.sidebar.tab_changed.connect(self._on_tab_changed)
            mid_h_layout.addWidget(self.sidebar)

            # Center Stacked Views
            self.stacked_views = QStackedWidget(mid_widget)
            
            self.console_view = ConsoleView(self.stacked_views)
            self.tasks_view = TasksView(self.stacked_views)
            self.agents_view = AgentsView(self.stacked_views)
            self.computer_view = ComputerView(self.stacked_views)
            self.memory_view = MemoryView(self.stacked_views)
            self.security_view = SecurityView(self.stacked_views)
            self.recovery_view = RecoveryView(self.stacked_views)
            self.system_view = SystemView(self.stacked_views)

            self.tab_index_map = {
                NavigationTab.CONSOLE: self.stacked_views.addWidget(self.console_view),
                NavigationTab.TASKS: self.stacked_views.addWidget(self.tasks_view),
                NavigationTab.AGENTS: self.stacked_views.addWidget(self.agents_view),
                NavigationTab.COMPUTER: self.stacked_views.addWidget(self.computer_view),
                NavigationTab.MEMORY: self.stacked_views.addWidget(self.memory_view),
                NavigationTab.SECURITY: self.stacked_views.addWidget(self.security_view),
                NavigationTab.RECOVERY: self.stacked_views.addWidget(self.recovery_view),
                NavigationTab.SYSTEM: self.stacked_views.addWidget(self.system_view),
            }

            mid_h_layout.addWidget(self.stacked_views, stretch=1)

            # Right System Monitor
            self.monitor = SystemMonitorWidget(mid_widget)
            mid_h_layout.addWidget(self.monitor)

            main_v_layout.addWidget(mid_widget, stretch=1)

            # Bottom Command Input Bar
            self.input_bar = CommandInputWidget(central)
            if self.controller:
                self.input_bar.command_submitted.connect(self.controller.handle_user_command)
                self.input_bar.voice_toggled.connect(self.controller.handle_voice_toggle)
                self.input_bar.emergency_stop_triggered.connect(self.controller.handle_emergency_stop)
                self.monitor.autonomy_changed.connect(self.controller.handle_autonomy_change)
                self.security_view.approval_responded.connect(self.controller.handle_approval_response)

            main_v_layout.addWidget(self.input_bar)

            # Setup System Tray Integration
            self._setup_system_tray()

        def _on_tab_changed(self, tab: NavigationTab):
            if tab in self.tab_index_map:
                idx = self.tab_index_map[tab]
                self.stacked_views.setCurrentIndex(idx)

        def _setup_system_tray(self):
            """Setup background operation tray icon."""
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("Nexus Agent Command Center")
            
            tray_menu = QMenu(self)
            show_action = QAction("Open Console", self)
            show_action.triggered.connect(self.showNormal)
            
            stop_action = QAction("🛑 Emergency Stop", self)
            if self.controller:
                stop_action.triggered.connect(self.controller.handle_emergency_stop)

            exit_action = QAction("Exit Nexus Agent", self)
            exit_action.triggered.connect(QApplication.quit)

            tray_menu.addAction(show_action)
            tray_menu.addAction(stop_action)
            tray_menu.addSeparator()
            tray_menu.addAction(exit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

        def update_ui_state(self, ui_state: UIState):
            """Update view components from latest UIState."""
            self.console_view.update_state(ui_state)
            self.monitor.update_metrics(ui_state.metrics)
            self.monitor.update_security_status(ui_state.pending_approvals_count)
            self.monitor.update_recovery_status(ui_state.recent_recovery_count, ui_state.is_emergency_stopped)
            self.sidebar.set_emergency_status(ui_state.is_emergency_stopped)

else:
    class NexusMainWindow:
        """Headless fallback for NexusMainWindow."""
        def __init__(self, controller=None):
            self.controller = controller
        def show(self):
            pass
        def update_ui_state(self, ui_state: UIState):
            pass
