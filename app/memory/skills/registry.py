from typing import Any
from .models import Skill, SkillInput, SkillStep


class SkillRegistry:
    """Manages discovery, registration, and selection of reusable high-level skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._register_default_skills()

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered.")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' is not registered.")
        return self._skills[name]

    def list_skills(self) -> list[dict[str, Any]]:
        return [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "required_tools": skill.required_tools,
            }
            for skill in self._skills.values()
        ]

    def find_matching_skill(self, goal: str) -> Skill | None:
        lower_goal = goal.lower()
        if "python project" in lower_goal or "python app" in lower_goal:
            if "create_python_project" in self._skills:
                return self._skills["create_python_project"]
        return None

    def _register_default_skills(self) -> None:
        # Create Python Project Built-in Skill
        python_skill = Skill(
            id="skill-create-python-proj",
            name="create_python_project",
            description="Creates a standard Python project with src/, tests/, README.md, and requirements.txt.",
            version="1.0.0",
            inputs=[
                SkillInput(name="project_name", description="Name of the Python project"),
                SkillInput(name="parent_dir", description="Parent directory path", required=False, default="./workspace"),
            ],
            required_tools=["create_directory", "write_file"],
            steps=[
                SkillStep(
                    id="step-1",
                    tool_name="create_directory",
                    input_template={"path": "{parent_dir}/{project_name}/src"},
                    expected_state={"exists": True, "is_directory": True},
                ),
                SkillStep(
                    id="step-2",
                    tool_name="create_directory",
                    input_template={"path": "{parent_dir}/{project_name}/tests"},
                    expected_state={"exists": True, "is_directory": True},
                ),
                SkillStep(
                    id="step-3",
                    tool_name="write_file",
                    input_template={"path": "{parent_dir}/{project_name}/README.md", "content": "# {project_name}\n\nPython project created by Agentic Computer OS."},
                    expected_state={"exists": True},
                ),
                SkillStep(
                    id="step-4",
                    tool_name="write_file",
                    input_template={"path": "{parent_dir}/{project_name}/requirements.txt", "content": "# Dependencies\n"},
                    expected_state={"exists": True},
                ),
            ],
        )
        self.register(python_skill)
