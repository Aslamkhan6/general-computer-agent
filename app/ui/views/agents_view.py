"""
Multi-Agent Network View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
        QGridLayout, QProgressBar
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class AgentsView(QWidget):
        """View displaying Supervisor and specialized Worker Agent topology."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(12)

            header = QLabel("SUPERVISOR & MULTI-AGENT WORKER NETWORK", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            grid = QGridLayout()
            grid.setSpacing(10)

            agents = [
                ("👑 Supervisor Core", "Orchestration & Task Dispatcher", "#00f0ff"),
                ("🔍 ResearchAgent", "Web Search, Codebase & Document Analysis", "#3b82f6"),
                ("💻 CodingAgent", "File Operations, Python, Refactoring", "#10b981"),
                ("🖱️ ComputerAgent", "GUI Automation, Vision & Accessibility", "#f59e0b"),
                ("🌐 BrowserAgent", "Headless Navigation, Web GUI Automation", "#ec4899"),
                ("✅ VerificationAgent", "State Validation & Artifact Checking", "#8b5cf6"),
            ]

            self.agent_cards = {}
            for index, (title, desc, color) in enumerate(agents):
                card = QGroupBox(title, self)
                card.setStyleSheet(f"QGroupBox::title {{ color: {color}; }}")
                c_layout = QVBoxLayout(card)

                desc_label = QLabel(desc, card)
                desc_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
                c_layout.addWidget(desc_label)

                status_label = QLabel("Status: READY / IDLE", card)
                status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
                c_layout.addWidget(status_label)

                self.agent_cards[title] = status_label

                row = index // 2
                col = index % 2
                grid.addWidget(card, row, col)

            layout.addLayout(grid)
            layout.addStretch()

        def update_agent_status(self, agent_role: str, status: str):
            """Update status label of a worker card."""
            for key, label in self.agent_cards.items():
                if agent_role.lower() in key.lower():
                    label.setText(f"Status: {status}")

else:
    class AgentsView:
        """Headless fallback for AgentsView."""
        def __init__(self, parent=None):
            pass
        def update_agent_status(self, agent_role: str, status: str):
            pass
