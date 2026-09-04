from typing import Any
from .models import AgentMessage


class MessageBus:
    """Structured Agent-to-Agent communication channel routed strictly through Supervisor."""

    def __init__(self):
        self._messages: list[AgentMessage] = []

    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        task_id: str,
        content: str,
        message_type: str = "RESULT",
        payload: dict[str, Any] | None = None,
    ) -> AgentMessage:
        msg = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            task_id=task_id,
            content=content,
            message_type=message_type,
            payload=payload or {},
        )
        self._messages.append(msg)
        return msg

    def get_messages_for_agent(self, agent_id: str) -> list[AgentMessage]:
        return [m for m in self._messages if m.receiver_id == agent_id or m.receiver_id == "SUPERVISOR"]

    def get_messages_for_task(self, task_id: str) -> list[AgentMessage]:
        return [m for m in self._messages if m.task_id == task_id]
