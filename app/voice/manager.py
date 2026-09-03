from typing import Any

from app.agent.controller import AgentController
from app.core.state import AgentTask
from app.planner.planner import Planner
from .audio import AudioCapture, AudioBuffer
from .command import VoiceCommandProcessor
from .interruption import VoiceInterruptionHandler
from .response import VoiceResponseManager
from .session import VoiceSessionManager, VoiceState
from .stt import STTEngine
from .tts import TTSEngine
from .wake_word import WakeWordDetector


class VoiceManager:
    """Unified Voice Intelligence Manager connecting Audio, STT, Session, Wake Word, TTS, and Agent Core."""

    def __init__(
        self,
        audio: AudioCapture | None = None,
        stt: STTEngine | None = None,
        command_processor: VoiceCommandProcessor | None = None,
        session_manager: VoiceSessionManager | None = None,
        tts: TTSEngine | None = None,
        response_manager: VoiceResponseManager | None = None,
        wake_word_detector: WakeWordDetector | None = None,
        interruption_handler: VoiceInterruptionHandler | None = None,
    ):
        self.audio = audio or AudioCapture()
        self.stt = stt or STTEngine()
        self.command_processor = command_processor or VoiceCommandProcessor()
        self.session = session_manager or VoiceSessionManager()
        self.tts = tts or TTSEngine()
        self.response_manager = response_manager or VoiceResponseManager()
        self.wake_word_detector = wake_word_detector or WakeWordDetector()
        self.interruption_handler = interruption_handler or VoiceInterruptionHandler()

    def process_audio_buffer(
        self,
        buffer: AudioBuffer,
        controller: AgentController,
        planner: Planner,
        task_id: str = "voice-task-001",
        speak_response: bool = True,
    ) -> dict[str, Any]:
        """Full end-to-end Voice -> STT -> Agent Core -> TTS pipeline."""

        # 1. Transcribe
        self.session.transition_to(VoiceState.TRANSCRIBING, details="Transcribing audio buffer")
        stt_res = self.stt.transcribe(buffer)

        if stt_res.is_silent or not stt_res.text:
            self.session.transition_to(VoiceState.IDLE, details="Silent audio input")
            return {"status": "silent", "transcript": "", "spoken": False}

        # 2. Wake Word Detection
        wake_res = self.wake_word_detector.detect(stt_res.text)
        command_text = wake_res.remaining_text if wake_res.detected else stt_res.text

        # 3. Clean Voice Command
        self.session.transition_to(VoiceState.PROCESSING, details="Processing voice command")
        processed_cmd = self.command_processor.process(command_text, confidence=stt_res.confidence)

        if processed_cmd.is_cancellation:
            self.session.transition_to(VoiceState.IDLE, details="Voice command cancelled by user")
            cancellation_msg = "Voice command cancelled."
            if speak_response:
                self.session.transition_to(VoiceState.SPEAKING)
                self.tts.speak(cancellation_msg)
                self.session.transition_to(VoiceState.IDLE)
            return {"status": "cancelled", "transcript": stt_res.text, "spoken": True}

        # 4. Route Command to Agent Core (Planner -> Controller)
        goal = processed_cmd.cleaned_command
        plan = planner.create_plan(goal)
        task = AgentTask(id=task_id, user_request=goal)

        completed_task = controller.run_plan(task, plan)

        # 5. Format & Synthesize Spoken Response
        spoken_text = self.response_manager.format_task_response(completed_task)

        if speak_response:
            self.session.transition_to(VoiceState.SPEAKING, details="Speaking task result")
            self.tts.speak(spoken_text)

        self.session.transition_to(VoiceState.IDLE, details="Voice pipeline complete")

        return {
            "status": "success" if completed_task.status == "COMPLETED" else "failed",
            "transcript": stt_res.text,
            "command": goal,
            "spoken_response": spoken_text,
            "task_id": completed_task.id,
            "task_status": completed_task.status.value,
        }
