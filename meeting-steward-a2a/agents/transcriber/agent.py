"""Transcriber agent."""

import logging
from datetime import datetime

from a2a_protocol import AgentRole, AgentMessage, GraphState
from a2a_protocol.schemas import MeetingState
from .tools import process_audio


logger = logging.getLogger(__name__)


def transcriber_node(state: GraphState) -> GraphState:
    """
    Transcriber agent node for LangGraph.
    
    Processes audio input and updates state with transcript and segments.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    logger.info("Transcriber agent starting...")
    
    meeting = state["meeting"]
    
    # Only process if input is audio
    if state["input_type"] != "audio":
        logger.info("Input is not audio, skipping transcription")
        return state
    
    if not meeting.audio_path:
        raise ValueError("Audio path not provided in meeting state")
    
    try:
        # Process audio
        full_transcript, utterances = process_audio(meeting.audio_path)
        
        # Update meeting state
        meeting.transcript_raw = full_transcript
        meeting.segments = utterances
        
        # Create agent message
        message = AgentMessage(
            from_agent=AgentRole.TRANSCRIBER.value,
            to_agent=AgentRole.SUMMARIZER.value,
            content=f"Transcription complete: {len(utterances)} segments, {len(full_transcript)} characters",
            payload={
                "segment_count": len(utterances),
                "transcript_length": len(full_transcript),
                "speakers": list(set(u.speaker for u in utterances))
            }
        )
        
        # Update state
        state["meeting"] = meeting
        state["messages"] = [message]  # LangGraph reducer will append to existing messages
        state["current_step"] = "transcription_complete"
        
        logger.info(f"Transcription complete: {len(utterances)} segments")
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise
    
    return state
