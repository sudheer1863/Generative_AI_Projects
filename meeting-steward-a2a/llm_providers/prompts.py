"""Prompts for different agents in the system."""

from typing import List

from a2a_protocol.schemas import Utterance


# System prompts for each agent role

SUMMARIZER_SYSTEM_PROMPT = """You are an expert meeting summarizer. Your task is to create concise, actionable executive summaries from meeting transcripts.

Focus on:
- Key topics discussed
- Important outcomes
- High-level decisions
- Next steps

Output ONLY valid JSON matching this schema:
{
  "bullets": ["summary point 1", "summary point 2", ...]
}

Be concise and actionable. Each bullet should be a complete sentence."""


DECISION_EXTRACTOR_SYSTEM_PROMPT = """You are an expert at extracting key decisions from meeting transcripts.

A decision is:
- A commitment to a specific course of action
- A resolution to a previously open question
- An approval or rejection of a proposal

For each decision, extract:
- Description: What was decided
- Owner: Who is responsible (if mentioned)
- Rationale: Why the decision was made (if mentioned)
- Timestamp: When in the meeting (if mentioned)

Output ONLY valid JSON matching this schema:
{
  "decisions": [
    {
      "description": "Decision text",
      "owner": "Person name or null",
      "rationale": "Reasoning or null",
      "timestamp": "Time reference or null"
    }
  ]
}

If no decisions are found, return {"decisions": []}."""


ACTION_ITEM_SYSTEM_PROMPT = """You are an expert at extracting action items from meeting transcripts.

An action item is:
- A specific task to be completed
- Has an assignee (owner) or can be assigned
- May have a due date or priority

For each action item, extract:
- Description: What needs to be done
- Owner: Who will do it (if mentioned)
- Due date: When it's due (if mentioned)
- Priority: low/medium/high (infer from context)

Output ONLY valid JSON matching this schema:
{
  "action_items": [
    {
      "description": "Task description",
      "owner": "Person name or null",
      "due_date": "Date reference or null",
      "priority": "low|medium|high"
    }
  ]
}

If no action items are found, return {"action_items": []}."""


def build_summarizer_prompt(transcript: str, segments: List[Utterance]) -> str:
    """
    Build prompt for the summarizer agent.
    
    Args:
        transcript: Raw transcript text
        segments: Diarized utterances (optional, for context)
        
    Returns:
        Formatted prompt
    """
    if segments:
        # Include speaker information
        formatted_transcript = "\n".join([
            f"[{seg.speaker}] {seg.text}" for seg in segments
        ])
    else:
        formatted_transcript = transcript
    
    return f"""Analyze this meeting transcript and create an executive summary.

TRANSCRIPT:
{formatted_transcript}

Provide a JSON response with 3-5 concise summary bullets."""


def build_decision_extractor_prompt(transcript: str, segments: List[Utterance]) -> str:
    """
    Build prompt for the decision extractor agent.
    
    Args:
        transcript: Raw transcript text
        segments: Diarized utterances
        
    Returns:
        Formatted prompt
    """
    if segments:
        formatted_transcript = "\n".join([
            f"[{seg.speaker}] {seg.text}" for seg in segments
        ])
    else:
        formatted_transcript = transcript
    
    return f"""Extract all key decisions from this meeting transcript.

TRANSCRIPT:
{formatted_transcript}

Provide a JSON response with all decisions found."""


def build_action_item_prompt(transcript: str, segments: List[Utterance]) -> str:
    """
    Build prompt for the action item agent.
    
    Args:
        transcript: Raw transcript text
        segments: Diarized utterances
        
    Returns:
        Formatted prompt
    """
    if segments:
        formatted_transcript = "\n".join([
            f"[{seg.speaker}] {seg.text}" for seg in segments
        ])
    else:
        formatted_transcript = transcript
    
    return f"""Extract all action items from this meeting transcript.

TRANSCRIPT:
{formatted_transcript}

Provide a JSON response with all action items found."""
