"""
Module 8 -- Security + Permissions package.
Provides Risk Analysis, Action Classification, Policy Engine, Permission Capabilities,
Human Approval Manager, Secret Detection & Redaction, Security Audit Logger, Restricted Sandbox,
and SecurityManager central authorization gate.
"""
from .models import (
    RiskLevel,
    OperationType,
    PermissionState,
    NormalizedAction,
    SecurityDecision,
)
from .risk import RiskAnalyzer
from .classifier import ActionClassifier
from .policy import PolicyEngine
from .permissions import PermissionManager
from .approval import HumanApprovalManager
from .secrets import SecretDetector
from .audit import SecurityAuditLogger
from .sandbox import RestrictedSandbox
from .manager import SecurityManager

__all__ = [
    "RiskLevel",
    "OperationType",
    "PermissionState",
    "NormalizedAction",
    "SecurityDecision",
    "RiskAnalyzer",
    "ActionClassifier",
    "PolicyEngine",
    "PermissionManager",
    "HumanApprovalManager",
    "SecretDetector",
    "SecurityAuditLogger",
    "RestrictedSandbox",
    "SecurityManager",
]
