"""LangGraph state definition."""

from typing import Annotated, List
from typing_extensions import TypedDict
from operator import add

from .schemas import MeetingState, AgentMessage


def add_agent_messages(left: List[AgentMessage], right: List[AgentMessage]) -> List[AgentMessage]:
    """
    Custom reducer for agent messages.
    
    Simply concatenates the lists.
    """
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return left + right


class GraphState(TypedDict):
    """
    State object for LangGraph execution.
    
    This state is passed between nodes in the graph.
    """
    
    # Core meeting state
    meeting: MeetingState
    
    # Agent messages with custom reducer
    messages: Annotated[List[AgentMessage], add_agent_messages]
    
    # Control flags
    input_type: str  # 'audio' or 'text'
    current_step: str  # Track current processing step

