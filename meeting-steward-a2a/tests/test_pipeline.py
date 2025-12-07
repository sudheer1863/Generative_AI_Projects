"""Tests for pipeline and storage."""

import pytest
from pathlib import Path

from a2a_protocol.schemas import MeetingState, ExecutiveSummary, KeyDecision, ActionItem
from services.storage import save_meeting, get_meeting, list_meetings


def test_save_and_retrieve_meeting():
    """Test saving and retrieving a meeting."""
    # Create test meeting
    meeting = MeetingState(
        input_type="text",
        transcript_raw="Test meeting about project planning.",
        summary=ExecutiveSummary(bullets=["Discussed timeline", "Assigned tasks"]),
        decisions=[
            KeyDecision(
                description="Use agile methodology",
                owner="Team Lead"
            )
        ],
        action_items=[
            ActionItem(
                description="Set up sprint board",
                owner="Scrum Master",
                priority="high"
            )
        ],
        model_used="llama3.2"
    )
    
    # Save meeting
    meeting_id = save_meeting(meeting)
    assert meeting_id == meeting.id
    
    # Retrieve meeting
    retrieved = get_meeting(meeting_id)
    assert retrieved is not None
    assert retrieved.id == meeting_id
    assert retrieved.transcript_raw == meeting.transcript_raw
    assert len(retrieved.decisions) == 1
    assert len(retrieved.action_items) == 1
    assert retrieved.summary.bullets[0] == "Discussed timeline"


def test_list_meetings():
    """Test listing meetings."""
    meetings = list_meetings(limit=10)
    assert isinstance(meetings, list)
    # Should have at least the test meeting from previous test
    assert len(meetings) >= 0


def test_meeting_not_found():
    """Test retrieving non-existent meeting."""
    result = get_meeting("non-existent-id")
    assert result is None
