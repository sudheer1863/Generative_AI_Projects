"""Steward coordinator - LangGraph orchestration."""

import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from a2a_protocol import GraphState, MeetingState
from agents import (
    transcriber_node,
    summarizer_node,
    decision_extractor_node,
    action_item_node,
)


logger = logging.getLogger(__name__)


def input_router(state: GraphState) -> Literal["transcriber", "summarizer"]:
    """
    Route based on input type.
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name
    """
    if state["input_type"] == "audio":
        return "transcriber"
    else:
        return "summarizer"


def build_meeting_graph() -> StateGraph:
    """
    Build the complete LangGraph for meeting processing.
    
    Returns:
        Compiled LangGraph
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("transcriber", transcriber_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("decision_extractor", decision_extractor_node)
    workflow.add_node("action_item", action_item_node)
    
    # Set conditional entry point based on input type
    workflow.set_conditional_entry_point(
        input_router,
        {
            "transcriber": "transcriber",
            "summarizer": "summarizer"
        }
    )
    
    # Define edges (workflow paths)
    # Audio path: transcriber -> summarizer -> decision_extractor -> action_item -> END
    workflow.add_edge("transcriber", "summarizer")
    
    # Text path (and continuation from audio): summarizer -> decision_extractor -> action_item -> END
    workflow.add_edge("summarizer", "decision_extractor")
    workflow.add_edge("decision_extractor", "action_item")
    workflow.add_edge("action_item", END)
    
    # Compile graph
    app = workflow.compile()
    
    logger.info("Meeting graph compiled successfully")
    
    return app


# Create global graph instance
meeting_graph = build_meeting_graph()
