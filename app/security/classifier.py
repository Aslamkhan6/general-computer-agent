from .models import NormalizedAction, OperationType, RiskLevel
from .risk import RiskAnalyzer


class ActionClassifier:
    """Normalizes tool execution calls into NormalizedAction and classifies them into risk levels."""

    def __init__(self, risk_analyzer: RiskAnalyzer | None = None):
        self.risk_analyzer = risk_analyzer or RiskAnalyzer()

    def normalize(self, tool_name: str, arguments: dict) -> NormalizedAction:
        target = str(arguments.get("path") or arguments.get("url") or arguments.get("command") or arguments.get("target") or "")
        op = OperationType.READ
        reversible = True
        sensitivity = "NORMAL"

        if any(kw in tool_name for kw in ["delete", "remove", "clean"]):
            op = OperationType.DELETE
            reversible = False
        elif any(kw in tool_name for kw in ["write", "create", "copy", "move", "rename"]):
            op = OperationType.CREATE
        elif any(kw in tool_name for kw in ["command", "powershell", "execute", "process"]):
            op = OperationType.EXECUTE
        elif any(kw in tool_name for kw in ["install"]):
            op = OperationType.INSTALL
        elif any(kw in tool_name for kw in ["send"]):
            op = OperationType.SEND

        if any(kw in target.lower() for kw in ["password", "secret", "token", "env", "credentials"]):
            sensitivity = "SENSITIVE"

        action = NormalizedAction(
            tool=tool_name,
            target=target,
            operation=op,
            reversible=reversible,
            data_sensitivity=sensitivity,
            metadata=arguments,
        )
        action.potential_impact = self.risk_analyzer.analyze(action)
        return action

    def classify(self, tool_name: str, arguments: dict) -> tuple[NormalizedAction, RiskLevel]:
        action = self.normalize(tool_name, arguments)
        return action, action.potential_impact
