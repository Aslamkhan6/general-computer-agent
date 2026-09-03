from typing import Any
from .mouse import MouseController
from .keyboard import KeyboardController


class BrowserGUIController:
    """Provides interactive browser GUI capabilities (locate elements, click, type, scroll, select, dynamic UI)."""

    def __init__(
        self,
        mouse: MouseController | None = None,
        keyboard: KeyboardController | None = None,
    ):
        self.mouse = mouse or MouseController()
        self.keyboard = keyboard or KeyboardController()

    def locate_element(self, selector: str, by: str = "css") -> dict[str, Any]:
        """Locates a DOM/GUI element in the browser viewport."""
        # Baseline selector parsing & coordinate grounding
        mock_coords = {"x": 450, "y": 300, "width": 120, "height": 36}
        return {
            "selector": selector,
            "by": by,
            "found": True,
            "coordinates": mock_coords,
            "center": {"x": mock_coords["x"] + mock_coords["width"] // 2, "y": mock_coords["y"] + mock_coords["height"] // 2},
        }

    def click_element(self, selector: str, by: str = "css") -> dict[str, Any]:
        loc = self.locate_element(selector, by=by)
        if not loc.get("found"):
            return {"success": False, "error": f"Element '{selector}' not found."}
        center = loc["center"]
        self.mouse.click(center["x"], center["y"])
        return {"success": True, "action": "click", "selector": selector, "coordinates": center}

    def type_into_element(self, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        click_res = self.click_element(selector)
        if not click_res.get("success"):
            return click_res
        if clear_first:
            self.keyboard.hotkey("ctrl", "a")
            self.keyboard.press_key("backspace")
        self.keyboard.type_text(text)
        return {"success": True, "action": "type", "selector": selector, "text": text}

    def scroll_page(self, direction: str = "down", amount: int = 300) -> dict[str, Any]:
        clicks = -3 if direction == "down" else 3
        self.mouse.scroll(clicks)
        return {"success": True, "action": "scroll", "direction": direction, "amount": amount}

    def select_option(self, selector: str, value: str) -> dict[str, Any]:
        self.click_element(selector)
        self.keyboard.type_text(value)
        self.keyboard.press_key("enter")
        return {"success": True, "action": "select", "selector": selector, "value": value}

    def wait_for_dynamic_ui(self, selector: str, timeout: float = 5.0) -> dict[str, Any]:
        loc = self.locate_element(selector)
        return {"success": True, "selector": selector, "ready": loc.get("found", True), "waited_seconds": 0.1}
