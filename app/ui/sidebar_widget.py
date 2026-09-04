"""
Left Navigation Sidebar Widget for Nexus Agent Command Center.
"""

from app.ui.models import NavigationTab

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QFrame
    from PySide6.QtCore import Signal, Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class SidebarWidget(QWidget):
        """Navigation sidebar providing quick switching between Nexus subsystems."""

        tab_changed = Signal(NavigationTab)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("SidebarWidget")
            self.setFixedWidth(200)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 15, 10, 15)
            layout.setSpacing(8)

            # Logo & Header
            logo_label = QLabel("🤖 NEXUS AGENT", self)
            logo_label.setObjectName("LogoLabel")
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

            sub_title = QLabel("REAL ROBOT COMMAND CENTER", self)
            sub_title.setStyleSheet("color: #4b5563; font-size: 9px; font-weight: bold; font-family: monospace;")
            sub_title.setAlignment(Qt.AlignCenter)
            layout.addWidget(sub_title)

            # Separator Line
            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: #1a2333; max-height: 1px;")
            layout.addWidget(line)

            layout.addSpacing(10)

            # Navigation Buttons
            self.button_group = QButtonGroup(self)
            self.button_group.setExclusive(True)

            self.tabs_info = [
                (NavigationTab.CONSOLE, "🖥️  Console"),
                (NavigationTab.TASKS, "📋  Tasks"),
                (NavigationTab.AGENTS, "🤖  Agents"),
                (NavigationTab.COMPUTER, "💻  Computer"),
                (NavigationTab.MEMORY, "🧠  Memory"),
                (NavigationTab.SECURITY, "🛡️  Security"),
                (NavigationTab.RECOVERY, "🔄  Recovery"),
                (NavigationTab.SYSTEM, "⚙️  System"),
            ]

            self.buttons = {}
            for index, (tab, text) in enumerate(self.tabs_info):
                btn = QPushButton(text, self)
                btn.setProperty("class", "NavButton")
                btn.setCheckable(True)
                if index == 0:
                    btn.setChecked(True)

                self.button_group.addButton(btn, index)
                self.buttons[tab] = btn
                layout.addWidget(btn)

            self.button_group.idClicked.connect(self._on_button_clicked)

            layout.addStretch()

            # Footer Status Badge
            self.status_badge = QLabel("● SYSTEM ONLINE", self)
            self.status_badge.setStyleSheet("color: #00ff88; font-size: 11px; font-weight: bold; padding: 5px;")
            self.status_badge.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.status_badge)

        def _on_button_clicked(self, id_val: int):
            tab, _ = self.tabs_info[id_val]
            self.tab_changed.emit(tab)

        def set_active_tab(self, tab: NavigationTab):
            """Programmatically switch active button."""
            if tab in self.buttons:
                self.buttons[tab].setChecked(True)

        def set_emergency_status(self, is_emergency: bool):
            """Update status badge color."""
            if is_emergency:
                self.status_badge.setText("🛑 EMERGENCY STOP")
                self.status_badge.setStyleSheet("color: #ff3366; font-size: 11px; font-weight: bold; padding: 5px;")
            else:
                self.status_badge.setText("● SYSTEM ONLINE")
                self.status_badge.setStyleSheet("color: #00ff88; font-size: 11px; font-weight: bold; padding: 5px;")

else:
    class SidebarWidget:
        """Headless fallback for SidebarWidget."""
        def __init__(self, parent=None):
            self.active_tab = NavigationTab.CONSOLE
        def set_active_tab(self, tab: NavigationTab):
            self.active_tab = tab
        def set_emergency_status(self, is_emergency: bool):
            pass
