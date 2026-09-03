import os
import subprocess
import sys
from typing import Any


class TTSEngine:
    """Converts text into spoken audio output using local speech synthesis engines."""

    def __init__(self, rate: int = 175, volume: float = 1.0, voice_id: str | None = None):
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self._pyttsx_engine = None

    def speak(self, text: str) -> dict[str, Any]:
        if not text.strip():
            return {"success": False, "error": "Empty text provided to TTS."}

        # 1. Try pyttsx3 local offline synthesis
        try:
            import pyttsx3
            if self._pyttsx_engine is None:
                self._pyttsx_engine = pyttsx3.init()
            self._pyttsx_engine.setProperty("rate", self.rate)
            self._pyttsx_engine.setProperty("volume", self.volume)
            if self.voice_id:
                self._pyttsx_engine.setProperty("voice", self.voice_id)
            self._pyttsx_engine.say(text)
            self._pyttsx_engine.runAndWait()
            return {"success": True, "engine": "pyttsx3", "text": text}
        except Exception:
            pass

        # 2. Native Windows PowerShell System.Speech.Synthesis fallback
        if sys.platform == "win32":
            try:
                escaped_text = text.replace("'", "''").replace('"', '`"')
                ps_script = f"""
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.Rate = 1
                $synth.Speak('{escaped_text}')
                """
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=10)
                return {"success": True, "engine": "System.Speech.Synthesis", "text": text}
            except Exception:
                pass

        # 3. Headless/Console fallback
        return {"success": True, "engine": "console_fallback", "text": text}

    def stop(self) -> None:
        if self._pyttsx_engine:
            try:
                self._pyttsx_engine.stop()
            except Exception:
                pass
