import unittest

from app.agent.controller import AgentController
from app.core.enums import ActionStatus, StepStatus, TaskStatus
from app.core.events import EventBus
from app.observer.filesystem import FilesystemObserver
from app.planner.planner import Planner
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.verifier.filesystem import FilesystemVerifier

from app.voice import (
    AudioCapture,
    STTEngine,
    VoiceCommandProcessor,
    VoiceSessionManager,
    VoiceState,
    TTSEngine,
    VoiceResponseManager,
    WakeWordDetector,
    VoiceInterruptionHandler,
    VoiceManager,
)


class TestModule5Voice(unittest.TestCase):

    def setUp(self):
        self.audio = AudioCapture()
        self.stt = STTEngine()
        self.command_processor = VoiceCommandProcessor()
        self.session = VoiceSessionManager()
        self.tts = TTSEngine()
        self.response = VoiceResponseManager()
        self.wake = WakeWordDetector()
        self.interrupt = VoiceInterruptionHandler()
        self.voice_manager = VoiceManager(
            audio=self.audio,
            stt=self.stt,
            command_processor=self.command_processor,
            session_manager=self.session,
            tts=self.tts,
            response_manager=self.response,
            wake_word_detector=self.wake,
            interruption_handler=self.interrupt,
        )

        # Core Agent runtime setup
        self.event_bus = EventBus()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.observer = FilesystemObserver()
        self.verifier = FilesystemVerifier()
        self.controller = AgentController(
            executor=self.executor,
            observer=self.observer,
            verifier=self.verifier,
            event_bus=self.event_bus,
        )
        self.planner = Planner()

    def test_5_1_audio_capture(self):
        mics = self.audio.discover_microphones()
        self.assertGreaterEqual(len(mics), 1)

        buf = self.audio.capture(duration_seconds=0.1)
        self.assertIsNotNone(buf.pcm_data)
        self.assertEqual(buf.sample_rate, 16000)

    def test_5_2_stt(self):
        buf = self.audio.capture(duration_seconds=0.1)
        result = self.stt.transcribe(buf)
        self.assertIsNotNone(result.text)
        self.assertGreaterEqual(result.confidence, 0.0)

    def test_5_3_voice_command_processor(self):
        raw = "uhh okay computer please Create a directory called Voice-Test"
        proc = self.command_processor.process(raw)
        self.assertFalse(proc.is_cancellation)
        self.assertTrue("create a directory called voice-test" in proc.cleaned_command.lower())


        cancel_raw = "stop that action"
        proc_cancel = self.command_processor.process(cancel_raw)
        self.assertTrue(proc_cancel.is_cancellation)

    def test_5_4_voice_session_manager(self):
        self.assertEqual(self.session.current_state, VoiceState.IDLE)

        self.session.transition_to(VoiceState.LISTENING)
        self.assertEqual(self.session.current_state, VoiceState.LISTENING)

        self.session.transition_to(VoiceState.RECORDING)
        self.assertEqual(self.session.current_state, VoiceState.RECORDING)

        history = self.session.get_history()
        self.assertGreaterEqual(len(history), 2)

    def test_5_5_tts(self):
        res = self.tts.speak("Hello from voice engine")
        self.assertTrue(res["success"])

    def test_5_6_voice_response_manager(self):
        from app.core.state import AgentTask
        task = AgentTask(id="t1", user_request="Create dir", status=TaskStatus.COMPLETED)
        formatted = self.response.format_task_response(task)
        self.assertIn("completed successfully", formatted)

    def test_5_7_wake_word_detector(self):
        detect_res = self.wake.detect("Hey computer, create a folder named AI-Voice")
        self.assertTrue(detect_res.detected)
        self.assertEqual(detect_res.wake_phrase, "hey computer")
        self.assertEqual(detect_res.remaining_text, "create a folder named AI-Voice")

    def test_5_8_voice_interruption_handler(self):
        res = self.interrupt.check_interruption("Please stop immediately")
        self.assertTrue(res.interrupted)
        self.assertEqual(res.trigger_word, "stop")

    def test_5_9_full_voice_agent_integration(self):
        buf = self.audio.capture(duration_seconds=0.1)
        res = self.voice_manager.process_audio_buffer(
            buffer=buf,
            controller=self.controller,
            planner=self.planner,
            task_id="test-voice-pipeline",
            speak_response=False,
        )
        self.assertIn(res["status"], ["success", "failed", "cancelled", "silent"])

    def test_5_10_voice_tools(self):
        tools = [t["name"] for t in self.registry.list_tools()]
        self.assertIn("voice_listen", tools)
        self.assertIn("voice_transcribe", tools)
        self.assertIn("voice_speak", tools)
        self.assertIn("voice_stop_speaking", tools)
        self.assertIn("voice_get_state", tools)


if __name__ == "__main__":
    unittest.main()
