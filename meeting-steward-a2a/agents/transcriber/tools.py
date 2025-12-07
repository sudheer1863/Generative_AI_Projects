"""Audio transcription and diarization tools."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

from pydub import AudioSegment
import soundfile as sf

from a2a_protocol.schemas import Utterance
from app_config import settings


logger = logging.getLogger(__name__)


def convert_audio_to_wav(audio_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to 16kHz mono WAV format.
    
    Args:
        audio_path: Path to input audio file
        output_path: Optional output path (default: temp file)
        
    Returns:
        Path to converted WAV file
    """
    try:
        # Load audio using pydub
        audio = AudioSegment.from_file(audio_path)
        
        # Convert to mono and set sample rate
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(settings.sample_rate)
        
        # Generate output path if not provided
        if output_path is None:
            base_name = Path(audio_path).stem
            output_path = f"data/uploads/{base_name}_converted.wav"
        
        # Export as WAV
        audio.export(output_path, format="wav")
        logger.info(f"Converted audio to WAV: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to convert audio: {e}")
        raise


def transcribe_with_whisper(audio_path: str) -> Tuple[str, List[dict]]:
    """
    Transcribe audio using faster-whisper.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Tuple of (full_transcript, segments_list)
    """
    try:
        from faster_whisper import WhisperModel
        
        # Initialize model
        model_size = settings.whisper_model
        logger.info(f"Loading Whisper model: {model_size}")
        
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Transcribe
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language="en"  # Can be made configurable
        )
        
        # Collect segments
        transcript_segments = []
        full_text = []
        
        for segment in segments:
            segment_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            transcript_segments.append(segment_dict)
            full_text.append(segment.text.strip())
        
        full_transcript = " ".join(full_text)
        logger.info(f"Transcription complete: {len(transcript_segments)} segments")
        
        return full_transcript, transcript_segments
        
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise


def transcribe_and_diarize_with_whisperx(audio_path: str) -> Tuple[str, List[Utterance]]:
    """
    Transcribe and diarize audio using WhisperX.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Tuple of (full_transcript, utterances with speaker labels)
    """
    try:
        import whisperx
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        logger.info(f"Loading WhisperX model on {device}")
        
        # Load audio
        audio = whisperx.load_audio(audio_path)
        
        # Transcribe with Whisper
        model = whisperx.load_model(settings.whisper_model, device, compute_type=compute_type)
        result = model.transcribe(audio, batch_size=16)
        
        # Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
        
        # Perform diarization if possible
        utterances = []
        try:
            # Diarization requires pyannote, which may not be configured
            diarize_model = whisperx.DiarizationPipeline(use_auth_token=settings.hf_token, device=device)
            diarize_segments = diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # Build utterances with speaker labels
            for segment in result["segments"]:
                speaker = segment.get("speaker", "SPEAKER_00")
                utterance = Utterance(
                    start=segment["start"],
                    end=segment["end"],
                    speaker=speaker,
                    text=segment["text"].strip()
                )
                utterances.append(utterance)
            
            logger.info(f"Diarization complete: {len(utterances)} utterances")
            
        except Exception as e:
            logger.warning(f"Diarization failed, using default speaker labels: {e}")
            
            # Fallback: use segments without speaker labels
            for segment in result["segments"]:
                utterance = Utterance(
                    start=segment["start"],
                    end=segment["end"],
                    speaker="SPEAKER_00",
                    text=segment["text"].strip()
                )
                utterances.append(utterance)
        
        # Build full transcript
        full_transcript = " ".join([u.text for u in utterances])
        
        return full_transcript, utterances
        
    except ImportError:
        logger.warning("WhisperX not available, falling back to faster-whisper")
        return transcribe_with_whisper_fallback(audio_path)
    except Exception as e:
        logger.error(f"WhisperX transcription failed: {e}")
        raise


def transcribe_with_whisper_fallback(audio_path: str) -> Tuple[str, List[Utterance]]:
    """
    Fallback transcription using faster-whisper without diarization.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Tuple of (full_transcript, utterances with default speaker)
    """
    full_transcript, segments = transcribe_with_whisper(audio_path)
    
    # Convert to Utterance objects with default speaker
    utterances = [
        Utterance(
            start=seg["start"],
            end=seg["end"],
            speaker="SPEAKER_00",
            text=seg["text"]
        )
        for seg in segments
    ]
    
    return full_transcript, utterances


def process_audio(audio_path: str, use_whisperx: bool = None) -> Tuple[str, List[Utterance]]:
    """
    Main audio processing function: convert, transcribe, and diarize.
    
    Args:
        audio_path: Path to input audio file
        use_whisperx: Whether to use WhisperX (defaults to settings)
        
    Returns:
        Tuple of (full_transcript, list of utterances)
    """
    use_whisperx = use_whisperx if use_whisperx is not None else settings.use_whisperx
    
    # Convert to WAV if necessary
    if not audio_path.endswith('.wav'):
        audio_path = convert_audio_to_wav(audio_path)
    
    # Transcribe and diarize
    if use_whisperx:
        try:
            return transcribe_and_diarize_with_whisperx(audio_path)
        except Exception as e:
            logger.warning(f"WhisperX failed, falling back to faster-whisper: {e}")
            return transcribe_with_whisper_fallback(audio_path)
    else:
        return transcribe_with_whisper_fallback(audio_path)
