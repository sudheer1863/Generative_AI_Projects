#!/usr/bin/env python3
"""Standalone script to run meeting analysis on text transcript."""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import run_flow_from_text


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage: python run_text_meeting.py <transcript_file_path>")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    
    if not Path(transcript_path).exists():
        print(f"Error: Transcript file not found: {transcript_path}")
        sys.exit(1)
    
    # Read transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    print(f"Processing transcript from: {transcript_path}")
    print(f"Transcript length: {len(transcript)} characters\n")
    
    try:
        # Run analysis
        meeting = run_flow_from_text(transcript)
        
        # Display results
        print("=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        if meeting.summary:
            for bullet in meeting.summary.bullets:
                print(f"  • {bullet}")
        else:
            print("  No summary generated")
        
        print("\n" + "=" * 80)
        print("KEY DECISIONS")
        print("=" * 80)
        if meeting.decisions:
            for i, dec in enumerate(meeting.decisions, 1):
                print(f"\n{i}. {dec.description}")
                if dec.owner:
                    print(f"   Owner: {dec.owner}")
                if dec.rationale:
                    print(f"   Rationale: {dec.rationale}")
        else:
            print("  No decisions found")
        
        print("\n" + "=" * 80)
        print("ACTION ITEMS")
        print("=" * 80)
        if meeting.action_items:
            for i, item in enumerate(meeting.action_items, 1):
                print(f"\n{i}. {item.description}")
                print(f"   Owner: {item.owner or 'N/A'}")
                print(f"   Due: {item.due_date or 'N/A'}")
                print(f"   Priority: {item.priority}")
        else:
            print("  No action items found")
        
        print("\n" + "=" * 80)
        print(f"Processing time: {meeting.processing_time:.2f}s")
        print(f"Meeting ID: {meeting.id}")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
