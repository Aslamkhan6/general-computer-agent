from datetime import datetime, timezone
from typing import Any

from app.agent.controller import AgentController
from app.core.enums import TaskStatus
from app.core.state import AgentTask, TaskStep
from app.memory.manager import MemoryManager
from app.planner.plan import TaskPlan
from app.recovery.manager import RecoveryEngine
from app.security.manager import SecurityManager

from .communication import MessageBus
from .context import SharedTaskContextManager
from .dispatcher import TaskDispatcher
from .health import HealthMonitor
from .models import (
    AgentResult,
    AgentRole,
    AgentStatus,
    SubTask,
    SupervisorState,
    WorkerAgentInfo,
)
from .registry import AgentRegistry
from .resources import ResourceManager
from .results import ResultManager
from .scheduler import TaskScheduler


class Supervisor:
    """Central Authority and Manager for Multi-Agent Task Decomposition, Capability Matching, Dispatch, Concurrency Locks, Verification, Security, and Recovery."""

    def __init__(
        self,
        controller: AgentController | None = None,
        registry: AgentRegistry | None = None,
        security_manager: SecurityManager | None = None,
        recovery_engine: RecoveryEngine | None = None,
        memory_manager: MemoryManager | None = None,
    ):
        self.registry = registry or AgentRegistry()
        self.dispatcher = TaskDispatcher(registry=self.registry)
        self.message_bus = MessageBus()
        self.context_manager = SharedTaskContextManager()
        self.result_manager = ResultManager()
        self.health_monitor = HealthMonitor(registry=self.registry)
        self.resource_manager = ResourceManager()
        self.scheduler = TaskScheduler()

        self.security_manager = security_manager or SecurityManager()
        self.recovery_engine = recovery_engine or RecoveryEngine()
        self.memory_manager = memory_manager or MemoryManager()
        self.controller = controller

        self.state = SupervisorState.IDLE

    def decompose_task(self, goal: str, parent_task_id: str) -> list[SubTask]:
        """Decomposes a high-level user goal into structured subtasks assigned to specialized roles."""
        lower_goal = goal.lower()
        subtasks = []

        if "python project" in lower_goal or "coding" in lower_goal or "code" in lower_goal or "mern" in lower_goal:
            s1 = SubTask(
                id=f"{parent_task_id}-sub-1",
                parent_task_id=parent_task_id,
                description=f"Create project structure for '{goal}'",
                assigned_role=AgentRole.CODING,
                required_capabilities=["create_directory", "write_file"],
                input_data={"path": "./workspace/custom_projects/project_app"},
            )
            s2 = SubTask(
                id=f"{parent_task_id}-sub-2",
                parent_task_id=parent_task_id,
                description=f"Verify created files for '{goal}'",
                assigned_role=AgentRole.VERIFICATION,
                required_capabilities=["verify_state"],
                dependencies=[s1.id],
                input_data={"path": "./workspace/custom_projects/project_app"},
            )
            subtasks = [s1, s2]
        elif "research" in lower_goal or "search" in lower_goal or "find" in lower_goal:
            s1 = SubTask(
                id=f"{parent_task_id}-sub-1",
                parent_task_id=parent_task_id,
                description=f"Research topic: {goal}",
                assigned_role=AgentRole.RESEARCH,
                required_capabilities=["research", "read_file"],
                input_data={"query": goal},
            )
            subtasks = [s1]
        else:
            s1 = SubTask(
                id=f"{parent_task_id}-sub-1",
                parent_task_id=parent_task_id,
                description=f"Execute task: {goal}",
                assigned_role=AgentRole.COMPUTER,
                required_capabilities=["mouse_click", "screen_capture"],
                input_data={"request": goal},
            )
            subtasks = [s1]

        return subtasks

    def execute_subtask_with_worker(self, worker: WorkerAgentInfo, subtask: SubTask) -> AgentResult:
        """Executes a single subtask using the worker agent via AgentController with Security & Recovery authorization."""
        if not self.controller:
            raise RuntimeError("AgentController must be bound to Supervisor to execute subtasks.")

        start_time = datetime.now(timezone.utc)
        worker.status = AgentStatus.RUNNING
        subtask.status = AgentStatus.RUNNING

        # Lock resources if path specified
        path_target = subtask.input_data.get("path")
        if path_target:
            locked, lock_msg = self.resource_manager.acquire_lock(path_target, worker.id)
            if not locked:
                worker.status = AgentStatus.FAILED
                subtask.status = AgentStatus.FAILED
                return AgentResult(
                    task_id=subtask.parent_task_id,
                    subtask_id=subtask.id,
                    agent_id=worker.id,
                    status=AgentStatus.FAILED,
                    verified=False,
                    errors=[lock_msg],
                )

        # Build TaskPlan for subtask
        if "create_directory" in subtask.required_capabilities:
            tool_name = "create_directory"
        elif worker.role == AgentRole.VERIFICATION:
            tool_name = "get_metadata"
        elif worker.role in (AgentRole.CODING, AgentRole.COMPUTER):
            tool_name = "write_file"
        else:
            tool_name = "read_file"

        step = TaskStep(
            id=f"step-{subtask.id}",
            description=subtask.description,
            tool_name=tool_name,
            input_data=subtask.input_data,
            expected_state={"exists": True},
        )
        plan = TaskPlan(goal=subtask.description, steps=[step])

        agent_task = AgentTask(id=subtask.id, user_request=subtask.description)
        completed_task = self.controller.run_plan(agent_task, plan)

        # Release resource lock
        if path_target:
            self.resource_manager.release_lock(path_target, worker.id)

        dur = (datetime.now(timezone.utc) - start_time).total_seconds()
        if completed_task.status == TaskStatus.COMPLETED:
            subtask.status = AgentStatus.COMPLETED
            self.health_monitor.record_success(worker.id)
            res = AgentResult(
                task_id=subtask.parent_task_id,
                subtask_id=subtask.id,
                agent_id=worker.id,
                status=AgentStatus.COMPLETED,
                output=completed_task.final_result or {},
                artifacts=[path_target] if path_target else [],
                execution_time_seconds=dur,
                verified=True,
            )
        else:
            subtask.status = AgentStatus.FAILED
            self.health_monitor.record_failure(worker.id)
            res = AgentResult(
                task_id=subtask.parent_task_id,
                subtask_id=subtask.id,
                agent_id=worker.id,
                status=AgentStatus.FAILED,
                output={},
                execution_time_seconds=dur,
                verified=False,
                errors=[completed_task.error or "Subtask execution failed."],
            )

        return res

    def run_supervisor_task(self, user_goal: str, task_id: str = "task-sup-001") -> dict[str, Any]:
        """Main Supervisor workflow coordinating decomposition, dispatch, execution, verification, and aggregation."""
        self.state = SupervisorState.RECEIVING_TASK
        self.context_manager.init_context(task_id, user_goal)

        self.state = SupervisorState.DECOMPOSING
        subtasks = self.decompose_task(user_goal, task_id)

        completed_subtask_ids = set()
        self.state = SupervisorState.DISPATCHING

        for subtask in subtasks:
            executable = self.scheduler.get_executable_subtasks(subtasks, completed_subtask_ids)
            if not executable and not self.scheduler.is_all_completed(subtasks):
                break

            for st in executable:
                self.state = SupervisorState.DISPATCHING
                worker = self.dispatcher.dispatch(st)

                self.message_bus.send_message(
                    sender_id="SUPERVISOR",
                    receiver_id=worker.id,
                    task_id=task_id,
                    content=f"Dispatched subtask '{st.description}'",
                )

                self.state = SupervisorState.MONITORING
                result = self.execute_subtask_with_worker(worker, st)
                self.result_manager.add_result(result)

                if result.status == AgentStatus.COMPLETED:
                    completed_subtask_ids.add(st.id)
                    self.context_manager.record_subtask_result(task_id, st.id, result.output, result.artifacts)

        self.state = SupervisorState.AGGREGATING
        aggregated = self.result_manager.aggregate(task_id, subtasks)

        self.state = SupervisorState.COMPLETED if aggregated["verified"] else SupervisorState.FAILED
        return aggregated
