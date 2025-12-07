"""Pipeline orchestration for meeting processing."""

import logging
import time
from typing import Optional

from a2a_protocol import GraphState, MeetingState
from agents.steward import meeting_graph
from app_config import settings
from .storage import save_meeting


logger = logging.getLogger(__name__)


def run_flow_from_audio(
    audio_path: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> MeetingState:
    """
    Run complete meeting analysis pipeline from audio file.
    
    Args:
        audio_path: Path to audio file
        model: LLM model name (defaults to settings)
        temperature: LLM temperature (defaults to settings)
        
    Returns:
        Completed MeetingState
    """
    logger.info(f"Starting audio flow for: {audio_path}")
    start_time = time.time()
    
    # Create initial meeting state
    meeting = MeetingState(
        input_type="audio",
        audio_path=audio_path,
        model_used=model or settings.model_name
    )
    
    # Create initial graph state
    initial_state: GraphState = {
        "meeting": meeting,
        "messages": [],
        "input_type": "audio",
        "current_step": "started"
    }
    
    try:
        # Run graph
        final_state = meeting_graph.invoke(initial_state)
        
        # Extract final meeting state
        final_meeting = final_state["meeting"]
        final_meeting.processing_time = time.time() - start_time
        
        # Save to database
        save_meeting(final_meeting)
        
        logger.info(f"Audio flow complete in {final_meeting.processing_time:.2f}s")
        
        return final_meeting
        
    except Exception as e:
        logger.error(f"Audio flow failed: {e}")
        raise


def run_flow_from_text(
    transcript: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> MeetingState:
    """
    Run complete meeting analysis pipeline from text transcript.
    
    Args:
        transcript: Meeting transcript text
        model: LLM model name (defaults to settings)
        temperature: LLM temperature (defaults to settings)
        
    Returns:
        Completed MeetingState
    """
    logger.info("Starting text flow")
    start_time = time.time()
    
    # Create initial meeting state
    meeting = MeetingState(
        input_type="text",
        transcript_raw=transcript,
        model_used=model or settings.model_name
    )
    
    # Create initial graph state
    initial_state: GraphState = {
        "meeting": meeting,
        "messages": [],
        "input_type": "text",
        "current_step": "started"
    }
    
    try:
        # Run graph
        final_state = meeting_graph.invoke(initial_state)
        
        # Extract final meeting state
        final_meeting = final_state["meeting"]
        final_meeting.processing_time = time.time() - start_time
        
        # Save to database
        save_meeting(final_meeting)
        
        logger.info(f"Text flow complete in {final_meeting.processing_time:.2f}s")
        
        return final_meeting
        
    except Exception as e:
        logger.error(f"Text flow failed: {e}")
        raise
