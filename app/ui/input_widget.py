"""
Bottom Command Input Bar for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
    from PySide6.QtCore import Signal, Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class CommandInputWidget(QWidget):
        """Bottom human-agent interface with text, voice, and emergency stop controls."""

        command_submitted = Signal(str)
        voice_toggled = Signal(bool)
        emergency_stop_triggered = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("InputWidget")
            self.setFixedHeight(64)

            layout = QHBoxLayout(self)
            layout.setContentsMargins(15, 10, 15, 10)
            layout.setSpacing(10)

            # Text input field
            self.input_field = QLineEdit(self)
            self.input_field.setPlaceholderText("Type instruction or goal for Nexus Agent (e.g., 'Create a folder VoiceTest')...")
            self.input_field.returnPressed.connect(self._on_submit)
            layout.addWidget(self.input_field, stretch=1)

            # Send Button
            self.send_button = QPushButton("Send  ➔", self)
            self.send_button.setProperty("class", "PrimaryButton")
            self.send_button.clicked.connect(self._on_submit)
            layout.addWidget(self.send_button)

            # Voice Button (Module 5 STT trigger)
            self.voice_button = QPushButton("🎤 Voice", self)
            self.voice_button.setProperty("class", "VoiceButton")
            self.voice_button.setCheckable(True)
            self.voice_button.toggled.connect(self._on_voice_toggled)
            layout.addWidget(self.voice_button)

            # Emergency Stop Button
            self.emergency_button = QPushButton("🛑 EMERGENCY STOP", self)
            self.emergency_button.setProperty("class", "EmergencyButton")
            self.emergency_button.clicked.connect(self._on_emergency_clicked)
            layout.addWidget(self.emergency_button)

        def _on_submit(self):
            text = self.input_field.text().strip()
            if text:
                self.command_submitted.emit(text)
                self.input_field.clear()

        def _on_voice_toggled(self, checked: bool):
            if checked:
                self.voice_button.setText("🎙️ Listening...")
            else:
                self.voice_button.setText("🎤 Voice")
            self.voice_toggled.emit(checked)

        def _on_emergency_clicked(self):
            self.emergency_stop_triggered.emit()

        def set_voice_recording(self, recording: bool):
            """Programmatically update voice button state."""
            self.voice_button.setChecked(recording)

else:
    class CommandInputWidget:
        """Headless fallback for CommandInputWidget."""
        def __init__(self, parent=None):
            pass
        def set_voice_recording(self, recording: bool):
            pass
