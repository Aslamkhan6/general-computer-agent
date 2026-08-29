import logging
import sys
from typing import Any
from .events import Event, EventBus


def setup_logger(name: str = "agent_logger", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class StructuredLogger:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or setup_logger()

    def handle_event(self, event: Event) -> None:
        msg = f"[{event.event_type.value}] task={event.task_id}"
        if event.step_id:
            msg += f" step={event.step_id}"
        if event.payload:
            msg += f" details={event.payload}"
        self.logger.info(msg)

    def attach(self, event_bus: EventBus) -> None:
        event_bus.subscribe(self.handle_event)
