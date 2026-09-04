"""
QSS Styling Theme for Nexus Agent Command Center Desktop UI.
"""

NEXUS_DARK_THEME = """
/* Global Application Style */
QWidget {
    background-color: #0b0f17;
    color: #e0e6ed;
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #080b11;
}

/* Sidebar Styles */
#SidebarWidget {
    background-color: #0d121d;
    border-right: 1px solid #1a2333;
}

#LogoLabel {
    color: #00f0ff;
    font-size: 18px;
    font-weight: bold;
    padding: 10px;
    letter-spacing: 1px;
}

QPushButton.NavButton {
    background-color: transparent;
    color: #8b9bb4;
    border: none;
    border-radius: 6px;
    padding: 10px 15px;
    text-align: left;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #141c2c;
    color: #00f0ff;
}

QPushButton.NavButton:checked {
    background-color: #1a263c;
    color: #00f0ff;
    border-left: 4px solid #00f0ff;
}

/* Right System Monitor Styles */
#MonitorWidget {
    background-color: #0d121d;
    border-left: 1px solid #1a2333;
    padding: 10px;
}

QGroupBox {
    border: 1px solid #1c2638;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
    color: #00f0ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #0d121d;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #1e2a3e;
    border-radius: 4px;
    text-align: center;
    background-color: #090d15;
    color: #ffffff;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077ff, stop:1 #00f0ff);
    border-radius: 3px;
}

/* Bottom Input Bar */
#InputWidget {
    background-color: #0d121d;
    border-top: 1px solid #1a2333;
    padding: 10px;
}

QLineEdit {
    background-color: #121926;
    border: 1px solid #1e2a3e;
    border-radius: 6px;
    padding: 8px 12px;
    color: #ffffff;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #00f0ff;
}

QPushButton.PrimaryButton {
    background-color: #00f0ff;
    color: #080b11;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}

QPushButton.PrimaryButton:hover {
    background-color: #33f3ff;
}

QPushButton.VoiceButton {
    background-color: #1e293b;
    color: #00f0ff;
    border: 1px solid #00f0ff;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton.VoiceButton:checked {
    background-color: #e11d48;
    color: #ffffff;
    border-color: #ff4d6d;
}

QPushButton.EmergencyButton {
    background-color: #b91c1c;
    color: #ffffff;
    border: 1px solid #ef4444;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton.EmergencyButton:hover {
    background-color: #dc2626;
}

/* Tables & Lists */
QTableWidget, QListWidget, QTextEdit {
    background-color: #0f1523;
    border: 1px solid #1e2a3e;
    border-radius: 6px;
    color: #d1d5db;
    gridline-color: #1a2436;
}

QHeaderView::section {
    background-color: #131b2c;
    color: #00f0ff;
    padding: 6px;
    border: 1px solid #1a2436;
    font-weight: bold;
}

QScrollBar:vertical {
    border: none;
    background-color: #0b0f17;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #1e2a3e;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00f0ff;
}

/* Robot Canvas Container */
#RobotCanvas {
    background-color: #080c14;
    border: 1px solid #162032;
    border-radius: 12px;
}
"""
