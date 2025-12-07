"""Data schemas for Meeting Steward A2A system."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Utterance(BaseModel):
    """A single speaker-tagged utterance from the transcript."""
    
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    speaker: str = Field(..., description="Speaker label (e.g., SPEAKER_00)")
    text: str = Field(..., description="Transcript text")


class ExecutiveSummary(BaseModel):
    """Executive summary of the meeting."""
    
    bullets: List[str] = Field(default_factory=list, description="Summary bullet points")


class KeyDecision(BaseModel):
    """A key decision made during the meeting."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique decision ID")
    description: str = Field(..., description="Decision description")
    owner: Optional[str] = Field(None, description="Person responsible")
    timestamp: Optional[str] = Field(None, description="When the decision was made")
    rationale: Optional[str] = Field(None, description="Reasoning behind the decision")


class ActionItem(BaseModel):
    """An action item extracted from the meeting."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique action item ID")
    description: str = Field(..., description="Action item description")
    owner: Optional[str] = Field(None, description="Person assigned")
    due_date: Optional[str] = Field(None, description="Due date")
    priority: str = Field(default="medium", description="Priority level (low/medium/high)")
    status: str = Field(default="pending", description="Status (pending/in_progress/completed)")


class AgentMessage(BaseModel):
    """A2A protocol message for inter-agent communication."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Message ID")
    from_agent: str = Field(..., description="Sending agent role")
    to_agent: str = Field(..., description="Receiving agent role")
    content: str = Field(..., description="Message content")
    payload: Optional[dict] = Field(None, description="Additional structured data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MeetingState(BaseModel):
    """Central state object for a meeting analysis."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Meeting ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    # Input
    input_type: str = Field(..., description="Type of input: 'audio' or 'text'")
    audio_path: Optional[str] = Field(None, description="Path to audio file if applicable")
    
    # Transcript data
    transcript_raw: str = Field(default="", description="Full raw transcript text")
    segments: List[Utterance] = Field(default_factory=list, description="Diarized utterances")
    
    # Artifacts
    summary: Optional[ExecutiveSummary] = Field(None, description="Executive summary")
    decisions: List[KeyDecision] = Field(default_factory=list, description="Key decisions")
    action_items: List[ActionItem] = Field(default_factory=list, description="Action items")
    
    # Agent communication log
    agent_messages: List[AgentMessage] = Field(default_factory=list, description="A2A message log")
    
    # Metadata
    model_used: Optional[str] = Field(None, description="LLM model used for analysis")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
