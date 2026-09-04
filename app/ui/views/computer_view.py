"""
Live Computer Screen & Vision Inspection View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
        QTreeWidget, QTreeWidgetItem, QPushButton, QSplitter
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap, QImage
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class ComputerView(QWidget):
        """View for inspecting live screen captures, mouse coordinates, and accessibility tree."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel("COMPUTER VISION & SCREEN MONITOR (MOD 4)", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            splitter = QSplitter(Qt.Horizontal, self)

            # Left Container: Screen Preview
            left_box = QGroupBox("SCREEN STREAM PREVIEW", self)
            l_layout = QVBoxLayout(left_box)

            self.screen_label = QLabel("Click 'Capture Screen' to grab live desktop view...", left_box)
            self.screen_label.setAlignment(Qt.AlignCenter)
            self.screen_label.setStyleSheet("background-color: #080c14; border: 1px solid #1e2a3e;")
            self.screen_label.setMinimumSize(400, 280)
            l_layout.addWidget(self.screen_label)

            info_layout = QHBoxLayout()
            self.mouse_label = QLabel("Mouse: (X: 0, Y: 0)", left_box)
            self.window_label = QLabel("Active Window: Main Console", left_box)
            info_layout.addWidget(self.mouse_label)
            info_layout.addWidget(self.window_label)
            l_layout.addLayout(info_layout)

            self.capture_btn = QPushButton("📸 Capture Screen Now", left_box)
            self.capture_btn.setProperty("class", "PrimaryButton")
            l_layout.addWidget(self.capture_btn)

            splitter.addWidget(left_box)

            # Right Container: Accessibility Tree Inspector
            right_box = QGroupBox("ACCESSIBILITY & UI TREE INSPECTOR", self)
            r_layout = QVBoxLayout(right_box)

            self.tree_widget = QTreeWidget(right_box)
            self.tree_widget.setHeaderLabels(["Role / Control", "Title / Value", "Bounds"])
            r_layout.addWidget(self.tree_widget)

            splitter.addWidget(right_box)
            splitter.setSizes([450, 300])

            layout.addWidget(splitter)

        def update_mouse_info(self, x: int, y: int, window_title: str = ""):
            """Update mouse coordinates and active window title."""
            self.mouse_label.setText(f"Mouse: (X: {x}, Y: {y})")
            if window_title:
                self.window_label.setText(f"Active Window: {window_title}")

        def set_screen_image(self, pixmap: QPixmap):
            """Display screenshot in stream preview."""
            scaled = pixmap.scaled(self.screen_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.screen_label.setPixmap(scaled)

else:
    class ComputerView:
        """Headless fallback for ComputerView."""
        def __init__(self, parent=None):
            pass
        def update_mouse_info(self, x: int, y: int, window_title: str = ""):
            pass
        def set_screen_image(self, pixmap):
            pass
