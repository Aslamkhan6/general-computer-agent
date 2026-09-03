from typing import Any
from app.core.enums import ActionStatus
from app.core.state import ActionResult, TaskStep
from app.observer.base import BaseObserver
from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest
from app.verifier.base import BaseVerifier


class AlternativeToolEngine:
    """Maps failing tools to alternative tools across filesystem, GUI, browser, terminal, and voice domains."""

    ALTERNATIVE_MAP = {
        "mouse_click": "inspect_ui_tree",
        "visual_grounding_click": "mouse_click",
        "browser_search": "open_url",
        "create_file": "write_file",
        "execute_command": "run_powershell",
    }

    def find_alternative_tool(self, tool_name: str) -> str | None:
        return self.ALTERNATIVE_MAP.get(tool_name)

    def execute_alternative(
        self,
        step: TaskStep,
        executor: ToolExecutor,
        observer: BaseObserver,
        verifier: BaseVerifier,
    ) -> tuple[bool, str | None, ActionResult | None, dict[str, Any] | None]:
        alt_tool = self.find_alternative_tool(step.tool_name)
        if not alt_tool:
            return False, None, None, None

        # Build alternative arguments mapping
        alt_args = dict(step.input_data)
        if alt_tool == "write_file" and "content" not in alt_args:
            alt_args["content"] = ""

        req = ToolRequest(tool_name=alt_tool, arguments=alt_args)
        res = executor.execute(req)

        if res.status != ActionStatus.SUCCESS:
            return False, alt_tool, res, None

        obs_path = alt_args.get("path", "")
        actual_state = observer.observe(path=obs_path)
        verified = verifier.verify(expected=step.expected_state, actual=actual_state)

        return verified, alt_tool, res, actual_state
