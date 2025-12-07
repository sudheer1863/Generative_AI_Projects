"""Tests for A2A protocol schemas and routing."""

import pytest
from datetime import datetime

from a2a_protocol import (
    AgentRole,
    AgentMessage,
    MeetingState,
    Utterance,
    ExecutiveSummary,
    KeyDecision,
    ActionItem,
    validate_route,
    get_next_agents
)


def test_utterance_creation():
    """Test Utterance model."""
    utterance = Utterance(
        start=0.0,
        end=5.5,
        speaker="SPEAKER_00",
        text="Hello, this is a test."
    )
    
    assert utterance.start == 0.0
    assert utterance.end == 5.5
    assert utterance.speaker == "SPEAKER_00"
    assert "test" in utterance.text


def test_executive_summary():
    """Test ExecutiveSummary model."""
    summary = ExecutiveSummary(bullets=["Point 1", "Point 2", "Point 3"])
    
    assert len(summary.bullets) == 3
    assert "Point 1" in summary.bullets


def test_key_decision():
    """Test KeyDecision model."""
    decision = KeyDecision(
        description="Approved new feature",
        owner="John Doe",
        rationale="Customer demand"
    )
    
    assert decision.description == "Approved new feature"
    assert decision.owner == "John Doe"
    assert decision.id is not None


def test_action_item():
    """Test ActionItem model."""
    item = ActionItem(
        description="Complete documentation",
        owner="Jane Smith",
        due_date="2024-12-31",
        priority="high"
    )
    
    assert item.description == "Complete documentation"
    assert item.priority == "high"
    assert item.status == "pending"


def test_agent_message():
    """Test AgentMessage creation."""
    message = AgentMessage(
        from_agent=AgentRole.SUMMARIZER.value,
        to_agent=AgentRole.DECISION_EXTRACTOR.value,
        content="Summary complete"
    )
    
    assert message.from_agent == "SUMMARIZER"
    assert message.to_agent == "DECISION_EXTRACTOR"
    assert message.id is not None


def test_meeting_state():
    """Test MeetingState creation."""
    meeting = MeetingState(
        input_type="text",
        transcript_raw="This is a test meeting."
    )
    
    assert meeting.input_type == "text"
    assert meeting.id is not None
    assert meeting.transcript_raw == "This is a test meeting."
    assert len(meeting.segments) == 0


def test_route_validation():
    """Test agent routing validation."""
    # Valid routes
    assert validate_route("SUMMARIZER", "DECISION_EXTRACTOR") == True
    assert validate_route("DECISION_EXTRACTOR", "ACTION_ITEM_AGENT") == True
    
    # Invalid routes
    assert validate_route("ACTION_ITEM_AGENT", "TRANSCRIBER") == False
    assert validate_route("INVALID", "SUMMARIZER") == False


def test_get_next_agents():
    """Test getting next agent options."""
    next_agents = get_next_agents("SUMMARIZER")
    
    assert "DECISION_EXTRACTOR" in next_agents
    assert "STEWARD" in next_agents
    
    # Invalid agent
    assert get_next_agents("INVALID") == []
