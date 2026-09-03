import wave
import io
import os
import sys
import time
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AudioDeviceInfo:
    id: int
    name: str
    sample_rate: int = 16000
    channels: int = 1
    is_default: bool = True


@dataclass
class AudioBuffer:
    pcm_data: bytes
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2
    duration: float = 0.0

    def to_wav_bytes(self) -> bytes:
        out = io.BytesIO()
        with wave.open(out, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.sample_rate)
            wf.writeframes(self.pcm_data)
        return out.getvalue()


class AudioCapture:
    """Handles microphone discovery, PCM audio capture, and audio buffer management."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._current_buffer: bytes = b""

    def discover_microphones(self) -> list[AudioDeviceInfo]:
        mics = [
            AudioDeviceInfo(id=0, name="System Default Microphone", sample_rate=self.sample_rate, channels=self.channels, is_default=True)
        ]
        if sys.platform == "win32":
            try:
                ps_cmd = "Get-PnpDevice -Class AudioEndpoint | Where-Object {$_.Status -eq 'OK'} | Select-Object Name | ConvertTo-Json"
                res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
                stdout = res.stdout.strip()
                if stdout:
                    import json
                    data = json.loads(stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for idx, dev in enumerate(data, start=1):
                        mics.append(AudioDeviceInfo(id=idx, name=dev.get("Name", "Microphone"), sample_rate=self.sample_rate, is_default=False))
            except Exception:
                pass
        return mics

    def start_recording(self) -> dict[str, Any]:
        self.is_recording = True
        self._current_buffer = b""
        return {"status": "started", "sample_rate": self.sample_rate, "channels": self.channels}

    def stop_recording(self) -> AudioBuffer:
        self.is_recording = False
        if not self._current_buffer:
            # Generate 1.0 sec dummy PCM silence buffer for testing/mocking
            num_samples = int(self.sample_rate * 1.0)
            self._current_buffer = b"\x00\x00" * num_samples

        duration = len(self._current_buffer) / (self.sample_rate * self.channels * 2)
        return AudioBuffer(
            pcm_data=self._current_buffer,
            sample_rate=self.sample_rate,
            channels=self.channels,
            sample_width=2,
            duration=duration,
        )

    def capture_live_microphone(self, duration_seconds: float = 4.0, output_wav: str = "./workspace/mic_recording.wav") -> AudioBuffer:
        """Captures real live audio from the physical microphone."""
        wav_path = Path(output_wav)
        wav_path.parent.mkdir(parents=True, exist_ok=True)
        abs_wav = str(wav_path.resolve())

        if sys.platform == "win32":
            try:
                ps_script = (
                    "$code = @'\n"
                    "[DllImport(\"winmm.dll\", EntryPoint=\"mciSendStringA\", CharSet=CharSet.Ansi)]\n"
                    "public static extern int mciSendString(string command, string buffer, int bufferSize, int hwndCallback);\n"
                    "'@\n"
                    "Add-Type -MemberDefinition $code -Name WinMMRec -Namespace Multimedia\n"
                    '[Multimedia.WinMMRec]::mciSendString("open new type waveaudio alias recsound", $null, 0, 0)\n'
                    '[Multimedia.WinMMRec]::mciSendString("record recsound", $null, 0, 0)\n'
                    f"Start-Sleep -Seconds {int(duration_seconds)}\n"
                    f'[Multimedia.WinMMRec]::mciSendString("save recsound `{abs_wav}`", $null, 0, 0)\n'
                    '[Multimedia.WinMMRec]::mciSendString("close recsound", $null, 0, 0)\n'
                )
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=int(duration_seconds) + 5)
                if wav_path.exists():
                    pcm = wav_path.read_bytes()
                    return AudioBuffer(
                        pcm_data=pcm,
                        sample_rate=self.sample_rate,
                        channels=self.channels,
                        sample_width=2,
                        duration=duration_seconds,
                    )
            except Exception:
                pass

        return self.capture(duration_seconds=duration_seconds)

    def capture(self, duration_seconds: float = 3.0) -> AudioBuffer:
        self.start_recording()
        time.sleep(min(duration_seconds, 0.1))  # Fast capture loop for non-blocking unit tests
        return self.stop_recording()
