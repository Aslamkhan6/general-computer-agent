from typing import Any

from app.core.enums import ActionStatus, RiskLevel
from app.core.state import ActionResult
from app.voice.manager import VoiceManager
from .base import BaseTool

_voice_manager = VoiceManager()


class VoiceListenTool(BaseTool):
    name = "voice_listen"
    description = "Capture audio input from microphone."
    risk_level = RiskLevel.LOW
    parameters = {"duration_seconds": "float (optional, default 3.0)"}

    def execute(self, duration_seconds: float = 3.0) -> ActionResult:
        try:
            buf = _voice_manager.audio.capture(duration_seconds=duration_seconds)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"duration": buf.duration, "sample_rate": buf.sample_rate, "bytes": len(buf.pcm_data)},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class VoiceTranscribeTool(BaseTool):
    name = "voice_transcribe"
    description = "Transcribe captured audio buffer using Speech-to-Text (STT)."
    risk_level = RiskLevel.LOW
    parameters = {"duration_seconds": "float (optional, default 3.0)"}

    def execute(self, duration_seconds: float = 3.0) -> ActionResult:
        try:
            buf = _voice_manager.audio.capture(duration_seconds=duration_seconds)
            stt_res = _voice_manager.stt.transcribe(buf)
            return ActionResult(
                status=ActionStatus.SUCCESS,
                output={"text": stt_res.text, "confidence": stt_res.confidence, "language": stt_res.language},
            )
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class VoiceSpeakTool(BaseTool):
    name = "voice_speak"
    description = "Speak text using Text-to-Speech (TTS)."
    risk_level = RiskLevel.LOW
    parameters = {"text": "string"}

    def execute(self, text: str) -> ActionResult:
        try:
            res = _voice_manager.tts.speak(text)
            return ActionResult(status=ActionStatus.SUCCESS, output=res)
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class VoiceStopSpeakingTool(BaseTool):
    name = "voice_stop_speaking"
    description = "Halt active speech synthesis."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            _voice_manager.tts.stop()
            return ActionResult(status=ActionStatus.SUCCESS, output={"stopped": True})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))


class VoiceGetStateTool(BaseTool):
    name = "voice_get_state"
    description = "Query current voice session manager state."
    risk_level = RiskLevel.LOW
    parameters = {}

    def execute(self) -> ActionResult:
        try:
            state = _voice_manager.session.current_state.value
            return ActionResult(status=ActionStatus.SUCCESS, output={"current_state": state})
        except Exception as exc:
            return ActionResult(status=ActionStatus.FAILED, error=str(exc))
