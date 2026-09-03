from typing import Any
from pydantic import BaseModel, Field
import uuid


class SkillInput(BaseModel):
    name: str
    description: str
    required: bool = True
    default: Any = None


class SkillStep(BaseModel):
    id: str
    tool_name: str
    input_template: dict[str, Any] = Field(default_factory=dict)
    expected_state: dict[str, Any] = Field(default_factory=dict)


class Skill(BaseModel):
    id: str = Field(default_factory=lambda: f"skill-{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    version: str = "1.0.0"
    inputs: list[SkillInput] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    steps: list[SkillStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
