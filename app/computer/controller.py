from typing import Any
from .accessibility import AccessibilityInspector
from .browser_gui import BrowserGUIController
from .keyboard import KeyboardController
from .mouse import MouseController
from .screen import ScreenManager, ScreenState
from .vision import VisionGroundingEngine
from .windows import WindowManager


class ComputerController:
    """Unified controller orchestrating Screen, Mouse, Keyboard, Windows, Accessibility, Browser GUI, and Vision."""

    def __init__(
        self,
        screen: ScreenManager | None = None,
        mouse: MouseController | None = None,
        keyboard: KeyboardController | None = None,
        windows: WindowManager | None = None,
        accessibility: AccessibilityInspector | None = None,
        browser: BrowserGUIController | None = None,
        vision: VisionGroundingEngine | None = None,
    ):
        self.screen = screen or ScreenManager()
        self.mouse = mouse or MouseController()
        self.keyboard = keyboard or KeyboardController()
        self.windows = windows or WindowManager()
        self.accessibility = accessibility or AccessibilityInspector()
        self.browser = browser or BrowserGUIController(self.mouse, self.keyboard)
        self.vision = vision or VisionGroundingEngine(self.screen, self.mouse)

    def get_state(self) -> dict[str, Any]:
        screen_state = self.screen.get_state()
        active_window = self.windows.get_active_window()
        return {
            "screen": {
                "width": screen_state.primary_width,
                "height": screen_state.primary_height,
                "monitors_count": len(screen_state.monitors),
            },
            "active_window": active_window.__dict__ if active_window else None,
        }

    def execute_gui_action(self, action_type: str, **kwargs: Any) -> dict[str, Any]:
        action_type = action_type.lower()
        if action_type == "click":
            return self.mouse.click(kwargs.get("x"), kwargs.get("y"), kwargs.get("button", "left"))
        elif action_type == "move":
            return self.mouse.move(kwargs.get("x", 0), kwargs.get("y", 0))
        elif action_type == "double_click":
            return self.mouse.double_click(kwargs.get("x"), kwargs.get("y"))
        elif action_type == "right_click":
            return self.mouse.right_click(kwargs.get("x"), kwargs.get("y"))
        elif action_type == "drag":
            return self.mouse.drag(kwargs.get("start_x", 0), kwargs.get("start_y", 0), kwargs.get("end_x", 0), kwargs.get("end_y", 0))
        elif action_type == "scroll":
            return self.mouse.scroll(kwargs.get("clicks", 0), kwargs.get("x"), kwargs.get("y"))
        elif action_type == "type":
            return self.keyboard.type_text(kwargs.get("text", ""))
        elif action_type == "press_key":
            return self.keyboard.press_key(kwargs.get("key", ""))
        elif action_type == "hotkey":
            return self.keyboard.hotkey(*kwargs.get("keys", []))
        elif action_type == "screenshot":
            path = self.screen.capture_screenshot(kwargs.get("output_path", "./workspace/screen.png"))
            return {"success": True, "path": path}
        elif action_type == "visual_click":
            return self.vision.execute_visual_click(kwargs.get("query", ""))
        elif action_type == "inspect_ui":
            return self.accessibility.inspect_ui_tree(kwargs.get("max_depth", 3))
        elif action_type == "window_focus":
            success = self.windows.focus(kwargs.get("target", ""))
            return {"success": success, "target": kwargs.get("target")}
        elif action_type == "window_close":
            success = self.windows.close(kwargs.get("target", ""))
            return {"success": success, "target": kwargs.get("target")}
        else:
            return {"success": False, "error": f"Unknown GUI action type: {action_type}"}
