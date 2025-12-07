"""Streamlit UI for Meeting Steward A2A."""

import logging
import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app_config import settings
from services import run_flow_from_audio, run_flow_from_text, list_meetings, get_meeting
from a2a_protocol.schemas import MeetingState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Page config
st.set_page_config(
    page_title="Meeting Steward A2A",
    page_icon="🎙️",
    layout="wide"
)


def init_session_state():
    """Initialize session state variables."""
    if "current_meeting" not in st.session_state:
        st.session_state.current_meeting = None
    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False


def display_summary(meeting: MeetingState):
    """Display executive summary."""
    st.subheader("📋 Executive Summary")
    
    if meeting.summary and meeting.summary.bullets:
        for bullet in meeting.summary.bullets:
            st.markdown(f"- {bullet}")
    else:
        st.info("No summary generated")


def display_decisions(meeting: MeetingState):
    """Display key decisions as a table."""
    st.subheader("🎯 Key Decisions")
    
    if meeting.decisions:
        decisions_data = []
        for dec in meeting.decisions:
            decisions_data.append({
                "Description": dec.description,
                "Owner": dec.owner or "N/A",
                "Rationale": dec.rationale or "N/A",
                "Timestamp": dec.timestamp or "N/A"
            })
        
        df = pd.DataFrame(decisions_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No decisions found")


def display_action_items(meeting: MeetingState):
    """Display action items as a table."""
    st.subheader("✅ Action Items")
    
    if meeting.action_items:
        items_data = []
        for item in meeting.action_items:
            items_data.append({
                "Description": item.description,
                "Owner": item.owner or "N/A",
                "Due Date": item.due_date or "N/A",
                "Priority": item.priority,
                "Status": item.status
            })
        
        df = pd.DataFrame(items_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No action items found")


def display_agent_log(meeting: MeetingState):
    """Display agent coordination log."""
    st.subheader("🤖 Agent Coordination Log")
    
    if meeting.agent_messages:
        log_data = []
        for msg in meeting.agent_messages:
            log_data.append({
                "Time": msg.timestamp.strftime("%H:%M:%S"),
                "From": msg.from_agent,
                "To": msg.to_agent,
                "Message": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            })
        
        df = pd.DataFrame(log_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No agent messages")


def display_transcript(meeting: MeetingState):
    """Display diarized transcript."""
    st.subheader("📝 Diarized Transcript")
    
    if meeting.segments:
        # Group by speaker
        speakers = {}
        for seg in meeting.segments:
            if seg.speaker not in speakers:
                speakers[seg.speaker] = []
            speakers[seg.speaker].append(seg.text)
        
        for speaker, texts in speakers.items():
            with st.expander(f"{speaker} ({len(texts)} utterances)"):
                for text in texts[:10]:  # Show first 10
                    st.markdown(f"- {text}")
                if len(texts) > 10:
                    st.markdown(f"*...and {len(texts) - 10} more*")
    elif meeting.transcript_raw:
        st.text_area("Raw Transcript", meeting.transcript_raw, height=200)
    else:
        st.info("No transcript available")


def main():
    """Main Streamlit app."""
    init_session_state()
    
    st.title("🎙️ Meeting Steward A2A")
    st.markdown("**Intelligent Multi-Agent Meeting Analysis**")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    model_name = st.sidebar.text_input(
        "Ollama Model",
        value=settings.model_name,
        help="LLM model name (e.g., llama3.2, mistral)"
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=settings.default_temperature,
        step=0.1,
        help="Controls randomness in LLM responses"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Recent Meetings")
    recent_meetings = list_meetings(limit=5)
    
    if recent_meetings:
        for mtg in recent_meetings:
            if st.sidebar.button(f"{mtg['created_at'][:16]} - {mtg['input_type']}", key=mtg['id']):
                loaded_meeting = get_meeting(mtg['id'])
                if loaded_meeting:
                    st.session_state.current_meeting = loaded_meeting
                    st.session_state.agent_messages = loaded_meeting.agent_messages
    
    # Main content area
    tab1, tab2 = st.tabs(["📥 New Analysis", "📊 Results"])
    
    with tab1:
        st.header("Input Selection")
        
        input_type = st.radio(
            "Select input type:",
            ["Audio File", "Text Transcript"],
            horizontal=True
        )
        
        if input_type == "Audio File":
            uploaded_file = st.file_uploader(
                "Upload meeting recording",
                type=["wav", "mp3", "m4a"],
                help="Supported formats: WAV, MP3, M4A"
            )
            
            if uploaded_file:
                # Show audio player
                st.audio(uploaded_file)
                
                # Save to temp location
                upload_path = Path("data/uploads") / uploaded_file.name
                upload_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(upload_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if st.button("🚀 Run Meeting Steward", type="primary", disabled=st.session_state.processing):
                    st.session_state.processing = True
                    
                    with st.spinner("Processing audio... This may take several minutes."):
                        try:
                            meeting = run_flow_from_audio(
                                str(upload_path),
                                model=model_name,
                                temperature=temperature
                            )
                            
                            st.session_state.current_meeting = meeting
                            st.session_state.agent_messages = meeting.agent_messages
                            st.success(f"✅ Processing complete in {meeting.processing_time:.2f}s")
                            
                        except Exception as e:
                            st.error(f"❌ Processing failed: {e}")
                            logger.error(f"Processing error: {e}", exc_info=True)
                        finally:
                            st.session_state.processing = False
        
        else:  # Text Transcript
            transcript_text = st.text_area(
                "Paste meeting transcript",
                height=300,
                placeholder="Enter the meeting transcript here..."
            )
            
            if st.button("🚀 Run Meeting Steward", type="primary", disabled=st.session_state.processing or not transcript_text):
                st.session_state.processing = True
                
                with st.spinner("Analyzing transcript..."):
                    try:
                        meeting = run_flow_from_text(
                            transcript_text,
                            model=model_name,
                            temperature=temperature
                        )
                        
                        st.session_state.current_meeting = meeting
                        st.session_state.agent_messages = meeting.agent_messages
                        st.success(f"✅ Analysis complete in {meeting.processing_time:.2f}s")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        logger.error(f"Analysis error: {e}", exc_info=True)
                    finally:
                        st.session_state.processing = False
    
    with tab2:
        if st.session_state.current_meeting:
            meeting = st.session_state.current_meeting
            
            # Display metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Input Type", meeting.input_type.upper())
            with col2:
                st.metric("Model Used", meeting.model_used or "N/A")
            with col3:
                st.metric("Processing Time", f"{meeting.processing_time:.2f}s" if meeting.processing_time else "N/A")
            
            st.markdown("---")
            
            # Display results
            display_summary(meeting)
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                display_decisions(meeting)
            with col2:
                display_action_items(meeting)
            
            st.markdown("---")
            display_agent_log(meeting)
            
            st.markdown("---")
            display_transcript(meeting)
            
        else:
            st.info("👈 Process a meeting to see results here")


if __name__ == "__main__":
    main()
