"""
Main entry point for General-Purpose Agentic Computer Operating System (Nexus Agent).
Boots Module 10 Desktop Command Center (PySide6 UI) or CLI Mode.
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.agent.controller import AgentController
from app.computer.controller import ComputerController
from app.core.events import EventBus
from app.core.logger import StructuredLogger
from app.memory.manager import MemoryManager
from app.observer.filesystem import FilesystemObserver
from app.planner.planner import Planner
from app.recovery.manager import RecoveryEngine
from app.security.manager import SecurityManager
from app.supervisor.supervisor import Supervisor
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier

# Module 10 UI Imports
from app.ui.controller import UIController
from app.ui.app_window import NexusMainWindow

try:
    from PySide6.QtWidgets import QApplication
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False


def run_cli_mode(supervisor: Supervisor, security_manager: SecurityManager):
    """Fallback CLI mode when --cli or --headless flag is specified."""
    print("==========================================================")
    print("      GENERAL-PURPOSE AGENTIC COMPUTER OS (CLI MODE)      ")
    print("==========================================================")

    workers = supervisor.registry.list_agents()
    print(f"\n[Module 9 -- Supervisor Active] Discovered {len(workers)} specialized worker agents:")
    for w in workers:
        print(f"  • [{w['role']}] {w['name']} (Capabilities: {', '.join(w['capabilities'][:3])}...)")

    multi_agent_goal = "Create a python project called MERN_App"
    print(f"\n--- Executing Multi-Agent Task under Supervisor: '{multi_agent_goal}' ---")
    sup_result = supervisor.run_supervisor_task(multi_agent_goal, task_id="task-sup-main-001")

    audit_logs = security_manager.audit_logger.get_logs()
    print(f"\n[Module 8 -- Audit Trail] Logged {len(audit_logs)} security decisions (Secrets Sanitized).")

    print("\n==========================================================")
    print(f" Supervisor State      : {supervisor.state.value}")
    print(f" Multi-Agent Result    : {sup_result['status'].value}")
    print(f" Subtasks Completed    : {sup_result['subtasks_completed']}/{sup_result['subtasks_total']}")
    print(f" Result Verified       : {sup_result['verified']}")
    print("==========================================================")


def main():
    # 1. Initialize core runtime & EventBus
    event_bus = EventBus()
    logger = StructuredLogger()
    logger.attach(event_bus)

    registry = ToolRegistry()
    register_all_default_tools(registry)

    executor = ToolExecutor(registry)
    observer = FilesystemObserver()
    verifier = FilesystemVerifier()

    # 2. Initialize Module 8 Security Manager & Module 7 Recovery Engine
    security_manager = SecurityManager()
    recovery_engine = RecoveryEngine(max_failures_per_step=3)

    controller = AgentController(
        executor=executor,
        observer=observer,
        verifier=verifier,
        event_bus=event_bus,
        recovery_engine=recovery_engine,
        security_manager=security_manager,
    )

    # 3. Initialize Module 9 Supervisor
    supervisor = Supervisor(
        controller=controller,
        security_manager=security_manager,
        recovery_engine=recovery_engine,
    )

    # CLI or Headless mode check
    is_cli = "--cli" in sys.argv or "--headless" in sys.argv
    if is_cli or not HAS_PYSIDE:
        run_cli_mode(supervisor, security_manager)
        return

    # 4. Launch Module 10 Real Robot Command Center UI (PySide6 Desktop App)
    print("==========================================================")
    print("      NEXUS AGENT — REAL ROBOT COMMAND CENTER (UI)        ")
    print("==========================================================")
    print(f"[Tool Discovery] Registered {len(registry.list_tools())} tools across all domains.")
    print("[Module 10 UI] Launching PySide6 Desktop Command Center GUI...")

    app = QApplication(sys.argv)
    
    ui_controller = UIController(
        supervisor=supervisor,
        agent_controller=controller,
        security_manager=security_manager,
        recovery_engine=recovery_engine,
        event_bus=event_bus,
    )
    
    main_window = NexusMainWindow(controller=ui_controller)
    ui_controller.state_updated.connect(main_window.update_ui_state)
    
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()