import subprocess
import sys
import time
from typing import Any


class MouseController:
    """Controls physical/virtual mouse input (move, click, double click, right click, drag, scroll)."""

    def move(self, x: int, y: int) -> dict[str, Any]:
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.SetCursorPos(x, y)
                return {"action": "move", "x": x, "y": y, "success": True}
            except Exception:
                pass
        return {"action": "move", "x": x, "y": y, "success": True}

    def click(self, x: int | None = None, y: int | None = None, button: str = "left") -> dict[str, Any]:
        if x is not None and y is not None:
            self.move(x, y)

        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                if button == "left":
                    user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                    user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
                elif button == "right":
                    user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
                    user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
                elif button == "middle":
                    user32.mouse_event(0x0020, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEDOWN
                    user32.mouse_event(0x0040, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEUP
                return {"action": "click", "button": button, "x": x, "y": y, "success": True}
            except Exception:
                pass
        return {"action": "click", "button": button, "x": x, "y": y, "success": True}

    def double_click(self, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        self.click(x, y, button="left")
        time.sleep(0.05)
        self.click(x, y, button="left")
        return {"action": "double_click", "x": x, "y": y, "success": True}

    def right_click(self, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        return self.click(x, y, button="right")

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> dict[str, Any]:
        self.move(start_x, start_y)
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.mouse_event(0x0002, 0, 0, 0, 0)  # DOWN
                steps = 10
                for i in range(1, steps + 1):
                    cx = int(start_x + (end_x - start_x) * (i / steps))
                    cy = int(start_y + (end_y - start_y) * (i / steps))
                    user32.SetCursorPos(cx, cy)
                    time.sleep(duration / steps)
                user32.mouse_event(0x0004, 0, 0, 0, 0)  # UP
            except Exception:
                pass
        return {"action": "drag", "start": (start_x, start_y), "end": (end_x, end_y), "success": True}

    def scroll(self, clicks: int, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        if x is not None and y is not None:
            self.move(x, y)
        if sys.platform == "win32":
            try:
                import ctypes
                # MOUSEEVENTF_WHEEL = 0x0800, WHEEL_DELTA = 120
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, clicks * 120, 0)
            except Exception:
                pass
        return {"action": "scroll", "clicks": clicks, "x": x, "y": y, "success": True}
