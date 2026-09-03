from time import perf_counter

from app.core.enums import ActionStatus
from app.core.state import ActionResult
from .registry import ToolRegistry
from .request import ToolRequest


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, request: ToolRequest) -> ActionResult:
        start_time = perf_counter()

        try:
            tool = self.registry.get(request.tool_name)

            result = tool.execute(**request.arguments)
            result.execution_time = perf_counter() - start_time
            result.tool_name = request.tool_name
            return result

        except KeyError as exc:
            return ActionResult(
                status=ActionStatus.FAILED,
                error=str(exc),
                execution_time=perf_counter() - start_time,
                tool_name=request.tool_name,
            )

        except TypeError as exc:
            return ActionResult(
                status=ActionStatus.FAILED,
                error=f"Invalid tool arguments: {exc}",
                execution_time=perf_counter() - start_time,
                tool_name=request.tool_name,
            )

        except Exception as exc:
            return ActionResult(
                status=ActionStatus.FAILED,
                error=str(exc),
                execution_time=perf_counter() - start_time,
                tool_name=request.tool_name,
            )