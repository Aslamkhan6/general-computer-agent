from app.agent.controller import AgentController
from app.core.events import EventBus
from app.core.logger import StructuredLogger
from app.core.state import AgentTask
from app.observer.filesystem import FilesystemObserver
from app.planner.planner import Planner
from app.tools.executor import ToolExecutor
from app.tools.filesystem import CreateDirectoryTool
from app.tools.registry import ToolRegistry
from app.verifier.filesystem import FilesystemVerifier


def main():
    print("=== AGENTIC COMPUTER OS RUNTIME ===")

    # 1. Initialize core system components
    event_bus = EventBus()
    logger = StructuredLogger()
    logger.attach(event_bus)

    registry = ToolRegistry()
    registry.register(CreateDirectoryTool())

    executor = ToolExecutor(registry)
    observer = FilesystemObserver()
    verifier = FilesystemVerifier()

    controller = AgentController(
        executor=executor,
        observer=observer,
        verifier=verifier,
        event_bus=event_bus,
    )

    planner = Planner()

    # 2. Define task and plan
    user_goal = "Create a directory called AI-Agent"
    print(f"\nUser Goal: '{user_goal}'")

    task = AgentTask(
        id="task-101",
        user_request=user_goal,
    )

    plan = planner.create_plan(user_goal)

    print("\n--- Generated Plan ---")
    for step in plan.steps:
        print(f"Step [{step.id}]: {step.description} (Tool: {step.tool_name})")

    # 3. Execute plan via Controller
    print("\n--- Executing Task ---")
    completed_task = controller.run_plan(task, plan)

    print("\n--- Final Task Summary ---")
    print(f"Task ID: {completed_task.id}")
    print(f"Status: {completed_task.status}")
    print(f"Final Result: {completed_task.final_result}")
    if completed_task.error:
        print(f"Error: {completed_task.error}")


if __name__ == "__main__":
    main()