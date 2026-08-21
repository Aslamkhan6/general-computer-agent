from typing import Any

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)