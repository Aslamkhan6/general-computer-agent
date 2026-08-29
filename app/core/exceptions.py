class AgentError(Exception):
    """Base exception for all agent runtime errors."""
    pass


class PlanningError(AgentError):
    """Raised when the planner fails to create a valid plan."""
    pass


class ExecutionError(AgentError):
    """Raised when tool execution fails."""
    pass


class VerificationError(AgentError):
    """Raised when verification checks fail."""
    pass


class ToolNotFoundError(AgentError):
    """Raised when a requested tool is not found in the registry."""
    pass
