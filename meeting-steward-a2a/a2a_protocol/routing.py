"""Routing logic for A2A protocol."""

from typing import Dict, List, Set

from .roles import AgentRole


# Define allowed agent-to-agent message flows
ALLOWED_ROUTES: Dict[AgentRole, Set[AgentRole]] = {
    AgentRole.SYSTEM: {
        AgentRole.STEWARD,
        AgentRole.TRANSCRIBER,
        AgentRole.SUMMARIZER,
    },
    AgentRole.STEWARD: {
        AgentRole.TRANSCRIBER,
        AgentRole.SUMMARIZER,
        AgentRole.DECISION_EXTRACTOR,
        AgentRole.ACTION_ITEM_AGENT,
    },
    AgentRole.TRANSCRIBER: {
        AgentRole.STEWARD,
        AgentRole.SUMMARIZER,
    },
    AgentRole.SUMMARIZER: {
        AgentRole.STEWARD,
        AgentRole.DECISION_EXTRACTOR,
    },
    AgentRole.DECISION_EXTRACTOR: {
        AgentRole.STEWARD,
        AgentRole.ACTION_ITEM_AGENT,
    },
    AgentRole.ACTION_ITEM_AGENT: {
        AgentRole.STEWARD,
    },
}


def validate_route(from_agent: str, to_agent: str) -> bool:
    """
    Validate if a message route is allowed.
    
    Args:
        from_agent: Sending agent role
        to_agent: Receiving agent role
        
    Returns:
        True if route is allowed, False otherwise
    """
    try:
        from_role = AgentRole(from_agent)
        to_role = AgentRole(to_agent)
        return to_role in ALLOWED_ROUTES.get(from_role, set())
    except ValueError:
        return False


def get_next_agents(current_agent: str) -> List[str]:
    """
    Get list of agents that can receive messages from the current agent.
    
    Args:
        current_agent: Current agent role
        
    Returns:
        List of allowed next agent roles
    """
    try:
        role = AgentRole(current_agent)
        return [agent.value for agent in ALLOWED_ROUTES.get(role, set())]
    except ValueError:
        return []
