"""
Main entry point for General-Purpose Agentic Computer Operating System.
Demonstrates Modules 1, 3, 4, 5, 6 (Memory & Skills), and 7 (Reliability + Recovery Engine) in unison.
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
from app.core.state import AgentTask, TaskStep
from app.memory.manager import MemoryManager
from app.memory.models import MemorySource, MemoryType
from app.memory.skills.manager import SkillManager
from app.observer.filesystem import FilesystemObserver
from app.planner.plan import TaskPlan
from app.planner.planner import Planner
from app.recovery.manager import RecoveryEngine
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier


def main():
    print("==========================================================")
    print("      GENERAL-PURPOSE AGENTIC COMPUTER OS RUNTIME         ")
    print("==========================================================")

    # 1. Initialize core runtime & EventBus
    event_bus = EventBus()
    logger = StructuredLogger()
    logger.attach(event_bus)

    registry = ToolRegistry()
    register_all_default_tools(registry)
    print(f"\n[Tool Discovery] Registered {len(registry.list_tools())} tools across all domains.")

    executor = ToolExecutor(registry)
    observer = FilesystemObserver()
    verifier = FilesystemVerifier()

    # 2. Initialize Module 7 Recovery Engine & Controller
    recovery_engine = RecoveryEngine(max_failures_per_step=3)
    controller = AgentController(
        executor=executor,
        observer=observer,
        verifier=verifier,
        event_bus=event_bus,
        recovery_engine=recovery_engine,
    )
    planner = Planner()

    # 3. Initialize Module 6 Memory & Skill System
    skill_mgr = SkillManager(controller=controller)
    memory_mgr = MemoryManager(skill_manager=skill_mgr)

    # Store User Preference Memory
    pref = memory_mgr.remember(
        content="Always create Python projects inside ./workspace/custom_projects",
        memory_type=MemoryType.USER_PREFERENCE,
        source=MemorySource.USER,
    )
    print(f"\n[Module 6 -- Memory Stored] ID: {pref.id} (Importance: {pref.importance})")

    # 4. Execute Skill Workflow with Module 7 Recovery Active
    user_goal = "Create my usual Python project called AI-Agent-System"
    mem_context = memory_mgr.retrieve_relevant_context(user_goal)
    print(f"[Module 6 -- Context Retrieval] Selected Skill: {mem_context['matching_skill']}")

    if mem_context['matching_skill']:
        print(f"\n--- Executing Selected Skill: '{mem_context['matching_skill']}' ---")
        completed_task = skill_mgr.execute_skill_by_name(
            skill_name=mem_context['matching_skill'],
            inputs={"project_name": "AI-Agent-System", "parent_dir": "./workspace/custom_projects"},
            task_id="task-skill-python-001",
        )
        memory_mgr.record_task_completion(completed_task)

    # 5. Demonstrate Module 7 Failure Recovery & Audit Trail
    print("\n[Module 7 -- Reliability + Recovery Demonstration]")
    rec_task = AgentTask(id="task-recovery-demo-001", user_request="Create resilience target file")
    rec_step = TaskStep(
        id="step-rec-001",
        description="Create resilience target file",
        tool_name="create_file",  # Triggers AlternativeToolEngine -> 'write_file'
        input_data={"path": "./workspace/recovery_demo.txt"},
        expected_state={"exists": True, "is_file": True},
    )
    rec_plan = TaskPlan(goal="Create resilience target file", steps=[rec_step])
    rec_completed = controller.run_plan(rec_task, rec_plan)

    recovery_records = recovery_engine.history.get_all_records()
    print(f"  • Recovery Engine Audit Records Logged: {len(recovery_records)}")

    print("\n==========================================================")
    print(f" Skill Task Status    : {completed_task.status}")
    print(f" Recovery Task Status : {rec_completed.status}")
    print("==========================================================")


if __name__ == "__main__":
    main()