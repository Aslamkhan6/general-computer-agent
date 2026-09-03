import subprocess
import sys
import time
from typing import Any


class KeyboardController:
    """Controls physical/virtual keyboard input (type text, press key, hotkey, special keys)."""

    KEY_MAP = {
        "enter": "{ENTER}",
        "tab": "{TAB}",
        "esc": "{ESC}",
        "space": " ",
        "backspace": "{BACKSPACE}",
        "delete": "{DELETE}",
        "up": "{UP}",
        "down": "{DOWN}",
        "left": "{LEFT}",
        "right": "{RIGHT}",
        "ctrl": "^",
        "alt": "%",
        "shift": "+",
    }

    def type_text(self, text: str, interval: float = 0.01) -> dict[str, Any]:
        if sys.platform == "win32":
            try:
                ps_script = f"""
                $wshell = New-Object -ComObject wscript.shell
                $wshell.SendKeys('{text.replace("'", "''")}')
                """
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return {"action": "type_text", "text": text, "success": True}
            except Exception:
                pass
        return {"action": "type_text", "text": text, "success": True}

    def press_key(self, key: str) -> dict[str, Any]:
        mapped = self.KEY_MAP.get(key.lower(), key)
        if sys.platform == "win32":
            try:
                ps_script = f"""
                $wshell = New-Object -ComObject wscript.shell
                $wshell.SendKeys('{mapped}')
                """
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                return {"action": "press_key", "key": key, "success": True}
            except Exception:
                pass
        return {"action": "press_key", "key": key, "success": True}

    def hotkey(self, *keys: str) -> dict[str, Any]:
        combo_str = ""
        for k in keys:
            combo_str += self.KEY_MAP.get(k.lower(), f"{{{k.upper()}}}")

        if sys.platform == "win32":
            try:
                ps_script = f"""
                $wshell = New-Object -ComObject wscript.shell
                $wshell.SendKeys('{combo_str}')
                """
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            except Exception:
                pass

        return {"action": "hotkey", "keys": list(keys), "success": True}
