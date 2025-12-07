"""LLM providers package."""

from .ollama_client import OllamaClient, ollama_client
from .prompts import (
    SUMMARIZER_SYSTEM_PROMPT,
    DECISION_EXTRACTOR_SYSTEM_PROMPT,
    ACTION_ITEM_SYSTEM_PROMPT,
    build_summarizer_prompt,
    build_decision_extractor_prompt,
    build_action_item_prompt,
)

__all__ = [
    "OllamaClient",
    "ollama_client",
    "SUMMARIZER_SYSTEM_PROMPT",
    "DECISION_EXTRACTOR_SYSTEM_PROMPT",
    "ACTION_ITEM_SYSTEM_PROMPT",
    "build_summarizer_prompt",
    "build_decision_extractor_prompt",
    "build_action_item_prompt",
]
