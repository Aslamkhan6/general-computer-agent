"""
Navigation Subviews for Nexus Agent Command Center.
"""

from app.ui.views.console_view import ConsoleView
from app.ui.views.tasks_view import TasksView
from app.ui.views.agents_view import AgentsView
from app.ui.views.computer_view import ComputerView
from app.ui.views.memory_view import MemoryView
from app.ui.views.security_view import SecurityView
from app.ui.views.recovery_view import RecoveryView
from app.ui.views.system_view import SystemView

__all__ = [
    "ConsoleView",
    "TasksView",
    "AgentsView",
    "ComputerView",
    "MemoryView",
    "SecurityView",
    "RecoveryView",
    "SystemView",
]
