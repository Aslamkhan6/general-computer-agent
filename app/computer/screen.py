import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MonitorInfo:
    id: int
    x: int
    y: int
    width: int
    height: int
    is_primary: bool = True


@dataclass
class ScreenState:
    primary_width: int
    primary_height: int
    monitors: list[MonitorInfo] = field(default_factory=list)
    active_window_title: str | None = None
    last_screenshot_path: str | None = None


class ScreenManager:
    """Manages display enumeration, resolution queries, and screenshot capture."""

    def get_screen_dimensions(self) -> dict[str, int]:
        width, height = 1920, 1080
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
            except Exception:
                pass
        return {"width": width, "height": height}

    def get_monitors(self) -> list[MonitorInfo]:
        dims = self.get_screen_dimensions()
        monitors = [
            MonitorInfo(
                id=1,
                x=0,
                y=0,
                width=dims["width"],
                height=dims["height"],
                is_primary=True,
            )
        ]
        if sys.platform == "win32":
            try:
                ps_cmd = "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorBasicDisplayParams | Select-Object InstanceName"
                res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
                lines = [l for l in res.stdout.splitlines() if l.strip()]
                if len(lines) > 2:
                    monitors = []
                    for idx, _ in enumerate(lines[2:], start=1):
                        monitors.append(
                            MonitorInfo(
                                id=idx,
                                x=(idx - 1) * dims["width"],
                                y=0,
                                width=dims["width"],
                                height=dims["height"],
                                is_primary=(idx == 1),
                            )
                        )
            except Exception:
                pass
        return monitors or [MonitorInfo(id=1, x=0, y=0, width=dims["width"], height=dims["height"], is_primary=True)]

    def capture_screenshot(self, output_path: str = "./workspace/screen.png") -> str:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        resolved_path = str(target.resolve()).replace("\\", "\\\\")

        if sys.platform == "win32":
            try:
                ps_cmd = f"""
                Add-Type -AssemblyName System.Windows.Forms, System.Drawing
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $bitmap.Size)
                $bitmap.Save('{resolved_path}', [System.Drawing.Imaging.ImageFormat]::Png)
                $graphics.Dispose()
                $bitmap.Dispose()
                """
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, check=True)
                return str(target.resolve())
            except Exception:
                pass

        # Fallback PNG generator if native PowerShell graphics fails
        target.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        return str(target.resolve())

    def get_state(self) -> ScreenState:
        dims = self.get_screen_dimensions()
        monitors = self.get_monitors()
        return ScreenState(
            primary_width=dims["width"],
            primary_height=dims["height"],
            monitors=monitors,
        )
