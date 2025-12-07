#!/usr/bin/env python3
"""Standalone script to transcribe and diarize audio."""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.transcriber.tools import process_audio


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <audio_file_path>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    if not Path(audio_path).exists():
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    print(f"Processing audio: {audio_path}")
    print("This may take several minutes...\n")
    
    try:
        # Process audio
        full_transcript, utterances = process_audio(audio_path)
        
        # Build output
        output = {
            "transcript": full_transcript,
            "utterances": [
                {
                    "start": u.start,
                    "end": u.end,
                    "speaker": u.speaker,
                    "text": u.text
                }
                for u in utterances
            ],
            "stats": {
                "total_utterances": len(utterances),
                "total_speakers": len(set(u.speaker for u in utterances)),
                "transcript_length": len(full_transcript)
            }
        }
        
        # Print JSON
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
