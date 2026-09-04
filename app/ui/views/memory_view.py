"""
Memory & Skill Registry View for Nexus Agent Command Center.
"""

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
        QTableWidgetItem, QGroupBox, QTabWidget, QHeaderView, QLineEdit, QPushButton
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    class QWidget: pass


if HAS_PYSIDE:
    class MemoryView(QWidget):
        """View displaying Module 6 Memory (Short-Term, Long-Term) and Skill Registry."""

        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel("INTELLIGENCE, MEMORY & SKILL REGISTRY (MOD 6)", self)
            header.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            tab_widget = QTabWidget(self)

            # Tab 1: Memories (Short & Long Term)
            mem_widget = QWidget(tab_widget)
            m_layout = QVBoxLayout(mem_widget)

            search_layout = QHBoxLayout()
            self.search_input = QLineEdit(mem_widget)
            self.search_input.setPlaceholderText("Search vector & SQLite memories...")
            self.search_btn = QPushButton("🔍 Search", mem_widget)
            search_layout.addWidget(self.search_input, stretch=1)
            search_layout.addWidget(self.search_btn)
            m_layout.addLayout(search_layout)

            self.mem_table = QTableWidget(0, 4, mem_widget)
            self.mem_table.setHorizontalHeaderLabels(["ID", "Content / Memory", "Type", "Importance Score"])
            self.mem_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            m_layout.addWidget(self.mem_table)

            tab_widget.addTab(mem_widget, "🧠 Memories")

            # Tab 2: Skill Registry
            skill_widget = QWidget(tab_widget)
            s_layout = QVBoxLayout(skill_widget)

            self.skill_table = QTableWidget(0, 4, skill_widget)
            self.skill_table.setHorizontalHeaderLabels(["Skill Name", "Domain", "Trigger Keywords", "Execution Count"])
            self.skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            s_layout.addWidget(self.skill_table)

            tab_widget.addTab(skill_widget, "⚡ Skill Registry")

            layout.addWidget(tab_widget)

        def set_memories(self, memories: list):
            """Populate memories table."""
            self.mem_table.setRowCount(len(memories))
            for i, m in enumerate(memories):
                self.mem_table.setItem(i, 0, QTableWidgetItem(str(m.get("id", ""))))
                self.mem_table.setItem(i, 1, QTableWidgetItem(str(m.get("content", ""))))
                self.mem_table.setItem(i, 2, QTableWidgetItem(str(m.get("memory_type", ""))))
                self.mem_table.setItem(i, 3, QTableWidgetItem(str(m.get("importance_score", 0.0))))

        def set_skills(self, skills: list):
            """Populate skills table."""
            self.skill_table.setRowCount(len(skills))
            for i, s in enumerate(skills):
                self.skill_table.setItem(i, 0, QTableWidgetItem(str(s.get("name", ""))))
                self.skill_table.setItem(i, 1, QTableWidgetItem(str(s.get("domain", ""))))
                self.skill_table.setItem(i, 2, QTableWidgetItem(str(s.get("triggers", ""))))
                self.skill_table.setItem(i, 3, QTableWidgetItem(str(s.get("execution_count", 0))))

else:
    class MemoryView:
        """Headless fallback for MemoryView."""
        def __init__(self, parent=None):
            pass
        def set_memories(self, memories: list):
            pass
        def set_skills(self, skills: list):
            pass
