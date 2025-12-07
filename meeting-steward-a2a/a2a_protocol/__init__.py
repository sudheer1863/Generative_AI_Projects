"""A2A protocol package."""

from .roles import AgentRole
from .routing import validate_route, get_next_agents, ALLOWED_ROUTES
from .schemas import (
    Utterance,
    ExecutiveSummary,
    KeyDecision,
    ActionItem,
    AgentMessage,
    MeetingState,
)
from .state import GraphState

__all__ = [
    "AgentRole",
    "validate_route",
    "get_next_agents",
    "ALLOWED_ROUTES",
    "Utterance",
    "ExecutiveSummary",
    "KeyDecision",
    "ActionItem",
    "AgentMessage",
    "MeetingState",
    "GraphState",
]
