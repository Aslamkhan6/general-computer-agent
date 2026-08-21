from pydantic import BaseModel, Field

from app.core.state import TaskStep


class TaskPlan(BaseModel):
    goal: str

    steps: list[TaskStep] = Field(
        default_factory=list
    )