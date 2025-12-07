"""Action item agent."""

import logging

from a2a_protocol import AgentRole, AgentMessage, GraphState
from a2a_protocol.schemas import ActionItem
from llm_providers import ollama_client, ACTION_ITEM_SYSTEM_PROMPT, build_action_item_prompt


logger = logging.getLogger(__name__)


def action_item_node(state: GraphState) -> GraphState:
    """
    Action item agent node for LangGraph.
    
    Extracts action items from transcript using LLM.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated graph state
    """
    logger.info("Action item agent starting...")
    
    meeting = state["meeting"]
    
    if not meeting.transcript_raw:
        raise ValueError("No transcript available for action item extraction")
    
    try:
        # Build prompt
        prompt = build_action_item_prompt(meeting.transcript_raw, meeting.segments)
        
        # Call LLM
        messages = [
            {"role": "system", "content": ACTION_ITEM_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = ollama_client.chat(messages, model=meeting.model_used)
        
        # Parse JSON response
        try:
            items_data = ollama_client.parse_json_response(response)
            items_list = items_data.get("action_items", [])
            
            action_items = []
            for item_data in items_list:
                action_item = ActionItem(
                    description=item_data.get("description", ""),
                    owner=item_data.get("owner"),
                    due_date=item_data.get("due_date"),
                    priority=item_data.get("priority", "medium"),
                    status="pending"
                )
                action_items.append(action_item)
                
        except Exception as e:
            logger.warning(f"Failed to parse structured action items: {e}")
            action_items = []
        
        # Update meeting state
        meeting.action_items = action_items
        
        # Create agent message
        message = AgentMessage(
            from_agent=AgentRole.ACTION_ITEM_AGENT.value,
            to_agent=AgentRole.STEWARD.value,
            content=f"Action item extraction complete: {len(action_items)} items found",
            payload={"action_item_count": len(action_items)}
        )
        
        # Update state
        state["meeting"] = meeting
        state["messages"] = [message]  # LangGraph reducer will append to existing messages
        state["current_step"] = "action_items_complete"
        
        logger.info(f"Action item extraction complete: {len(action_items)} items")
        
    except Exception as e:
        logger.error(f"Action item extraction failed: {e}")
        raise
    
    return state
