from typing import Any

from app.computer.controller import ComputerController
from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from .base import BaseTool


_computer_controller = ComputerController()


class ScreenCaptureTool(BaseTool):
    name = "screen_capture"
    description = "Capture desktop screenshot."
    risk_level = RiskLevel.LOW
    parameters = {"output_path": "string (optional, default ./workspace/screen.png)"}

    def execute(self, output_path: str = "./workspace/screen.png") -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("screenshot", output_path=output_path)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class MouseClickTool(BaseTool):
    name = "mouse_click"
    description = "Click mouse at specified screen coordinates (x, y) or button."
    risk_level = RiskLevel.MEDIUM
    parameters = {"x": "integer (optional)", "y": "integer (optional)", "button": "string (left|right|middle, default left)"}

    def execute(self, x: int | None = None, y: int | None = None, button: str = "left") -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("click", x=x, y=y, button=button)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class MouseMoveTool(BaseTool):
    name = "mouse_move"
    description = "Move mouse cursor to (x, y) coordinates."
    risk_level = RiskLevel.LOW
    parameters = {"x": "integer", "y": "integer"}

    def execute(self, x: int, y: int) -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("move", x=x, y=y)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class KeyboardTypeTool(BaseTool):
    name = "keyboard_type"
    description = "Type text input."
    risk_level = RiskLevel.MEDIUM
    parameters = {"text": "string"}

    def execute(self, text: str) -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("type", text=text)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class KeyboardHotkeyTool(BaseTool):
    name = "keyboard_hotkey"
    description = "Press key combinations/hotkey (e.g. ctrl, c)."
    risk_level = RiskLevel.MEDIUM
    parameters = {"keys": "list of strings"}

    def execute(self, keys: list[str]) -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("hotkey", keys=keys)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class WindowActionTool(BaseTool):
    name = "window_action"
    description = "Manage window state (focus, minimize, maximize, close)."
    risk_level = RiskLevel.MEDIUM
    parameters = {"action": "string (focus|minimize|maximize|close)", "target": "string"}

    def execute(self, action: str, target: str) -> ActionResult:
        try:
            act_type = f"window_{action.lower()}"
            res = _computer_controller.execute_gui_action(act_type, target=target)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class AccessibilityInspectTool(BaseTool):
    name = "inspect_ui_tree"
    description = "Inspect native OS accessibility UI element tree."
    risk_level = RiskLevel.LOW
    parameters = {"max_depth": "integer (optional, default 3)"}

    def execute(self, max_depth: int = 3) -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("inspect_ui", max_depth=max_depth)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class VisualGroundingClickTool(BaseTool):
    name = "visual_grounding_click"
    description = "Locate UI element on screen using Vision model grounding and click it."
    risk_level = RiskLevel.HIGH
    parameters = {"query": "string (description of element e.g. 'Submit button')"}

    def execute(self, query: str) -> ActionResult:
        try:
            res = _computer_controller.execute_gui_action("visual_click", query=query)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
