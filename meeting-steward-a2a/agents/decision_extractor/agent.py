"""Decision extractor agent."""

import logging

from a2a_protocol import AgentRole, AgentMessage, GraphState
from a2a_protocol.schemas import KeyDecision
from llm_providers import ollama_client, DECISION_EXTRACTOR_SYSTEM_PROMPT, build_decision_extractor_prompt


logger = logging.getLogger(__name__)


def decision_extractor_node(state: GraphState) -> GraphState:
    """
    Decision extractor agent node for LangGraph.
    
    Extracts key decisions from transcript using LLM.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    logger.info("Decision extractor agent starting...")
    
    meeting = state["meeting"]
    
    if not meeting.transcript_raw:
        raise ValueError("No transcript available for decision extraction")
    
    try:
        # Build prompt
        prompt = build_decision_extractor_prompt(meeting.transcript_raw, meeting.segments)
        
        # Call LLM
        messages = [
            {"role": "system", "content": DECISION_EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = ollama_client.chat(messages, model=meeting.model_used)
        
        # Parse JSON response
        try:
            decisions_data = ollama_client.parse_json_response(response)
            decisions_list = decisions_data.get("decisions", [])
            
            decisions = []
            for dec_data in decisions_list:
                decision = KeyDecision(
                    description=dec_data.get("description", ""),
                    owner=dec_data.get("owner"),
                    timestamp=dec_data.get("timestamp"),
                    rationale=dec_data.get("rationale")
                )
                decisions.append(decision)
                
        except Exception as e:
            logger.warning(f"Failed to parse structured decisions: {e}")
            decisions = []
        
        # Update meeting state
        meeting.decisions = decisions
        
        # Create agent message
        message = AgentMessage(
            from_agent=AgentRole.DECISION_EXTRACTOR.value,
            to_agent=AgentRole.ACTION_ITEM_AGENT.value,
            content=f"Decision extraction complete: {len(decisions)} decisions found",
            payload={"decision_count": len(decisions)}
        )
        
        # Update state
        state["meeting"] = meeting
        state["messages"] = [message]  # LangGraph reducer will append to existing messages
        state["current_step"] = "decision_extraction_complete"
        
        logger.info(f"Decision extraction complete: {len(decisions)} decisions")
        
    except Exception as e:
        logger.error(f"Decision extraction failed: {e}")
        raise
    
    return state
