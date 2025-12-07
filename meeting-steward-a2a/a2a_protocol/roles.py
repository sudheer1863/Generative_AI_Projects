"""Agent roles for A2A protocol."""

from enum import Enum


class AgentRole(str, Enum):
    """Enumeration of agent roles in the system."""
    
    STEWARD = "STEWARD"
    TRANSCRIBER = "TRANSCRIBER"
    SUMMARIZER = "SUMMARIZER"
    DECISION_EXTRACTOR = "DECISION_EXTRACTOR"
    ACTION_ITEM_AGENT = "ACTION_ITEM_AGENT"
    SYSTEM = "SYSTEM"  # For system-level messages
