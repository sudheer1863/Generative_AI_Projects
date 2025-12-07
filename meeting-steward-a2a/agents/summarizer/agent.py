"""Summarizer agent."""

import json
import logging

from a2a_protocol import AgentRole, AgentMessage, GraphState
from a2a_protocol.schemas import ExecutiveSummary
from llm_providers import ollama_client, SUMMARIZER_SYSTEM_PROMPT, build_summarizer_prompt


logger = logging.getLogger(__name__)


def summarizer_node(state: GraphState) -> GraphState:
    """
    Summarizer agent node for LangGraph.
    
    Generates executive summary from transcript using LLM.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    logger.info("Summarizer agent starting...")
    
    meeting = state["meeting"]
    
    if not meeting.transcript_raw:
        raise ValueError("No transcript available for summarization")
    
    try:
        # Build prompt
        prompt = build_summarizer_prompt(meeting.transcript_raw, meeting.segments)
        
        # Call LLM
        messages = [
            {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = ollama_client.chat(messages, model=meeting.model_used)
        
        # Parse JSON response
        try:
            summary_data = ollama_client.parse_json_response(response)
            summary = ExecutiveSummary(bullets=summary_data.get("bullets", []))
        except Exception as e:
            logger.warning(f"Failed to parse structured summary, using fallback: {e}")
            # Fallback: treat response as single bullet
            summary = ExecutiveSummary(bullets=[response.strip()])
        
        # Update meeting state
        meeting.summary = summary
        
        # Create agent message
        message = AgentMessage(
            from_agent=AgentRole.SUMMARIZER.value,
            to_agent=AgentRole.DECISION_EXTRACTOR.value,
            content=f"Summary complete: {len(summary.bullets)} bullet points",
            payload={"bullets": summary.bullets}
        )
        
        # Update state
        state["meeting"] = meeting
        state["messages"] = [message]  # LangGraph reducer will append to existing messages
        state["current_step"] = "summarization_complete"
        
        logger.info(f"Summarization complete: {len(summary.bullets)} bullets")
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise
    
    return state
