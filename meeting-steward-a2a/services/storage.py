"""SQLite storage layer for meeting data."""

import json
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from a2a_protocol.schemas import MeetingState, KeyDecision, ActionItem, ExecutiveSummary
from app_config import settings


logger = logging.getLogger(__name__)

Base = declarative_base()


class MeetingModel(Base):
    """SQLAlchemy model for meetings table."""
    
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    input_type = Column(String, nullable=False)
    audio_path = Column(String, nullable=True)
    transcript_raw = Column(Text, nullable=False)
    segments_json = Column(JSON, nullable=True)
    summary_json = Column(JSON, nullable=True)
    model_used = Column(String, nullable=True)
    processing_time = Column(String, nullable=True)


class DecisionModel(Base):
    """SQLAlchemy model for decisions table."""
    
    __tablename__ = "decisions"
    
    id = Column(String, primary_key=True)
    meeting_id = Column(String, nullable=False, index=True)
    data_json = Column(JSON, nullable=False)


class ActionItemModel(Base):
    """SQLAlchemy model for action items table."""
    
    __tablename__ = "action_items"
    
    id = Column(String, primary_key=True)
    meeting_id = Column(String, nullable=False, index=True)
    data_json = Column(JSON, nullable=False)


# Database setup
engine = create_engine(settings.db_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(engine)
    logger.info("Database initialized")


def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()


def save_meeting(meeting_state: MeetingState) -> str:
    """
    Save meeting state to database.
    
    Args:
        meeting_state: MeetingState object to save
        
    Returns:
        Meeting ID
    """
    session = get_session()
    
    try:
        # Serialize segments
        segments_json = [seg.model_dump() for seg in meeting_state.segments]
        
        # Serialize summary
        summary_json = meeting_state.summary.model_dump() if meeting_state.summary else None
        
        # Create meeting record
        meeting = MeetingModel(
            id=meeting_state.id,
            created_at=meeting_state.created_at,
            input_type=meeting_state.input_type,
            audio_path=meeting_state.audio_path,
            transcript_raw=meeting_state.transcript_raw,
            segments_json=segments_json,
            summary_json=summary_json,
            model_used=meeting_state.model_used,
            processing_time=str(meeting_state.processing_time) if meeting_state.processing_time else None
        )
        
        session.merge(meeting)
        
        # Save decisions
        for decision in meeting_state.decisions:
            dec_model = DecisionModel(
                id=decision.id,
                meeting_id=meeting_state.id,
                data_json=decision.model_dump()
            )
            session.merge(dec_model)
        
        # Save action items
        for action_item in meeting_state.action_items:
            item_model = ActionItemModel(
                id=action_item.id,
                meeting_id=meeting_state.id,
                data_json=action_item.model_dump()
            )
            session.merge(item_model)
        
        session.commit()
        logger.info(f"Saved meeting {meeting_state.id} to database")
        
        return meeting_state.id
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save meeting: {e}")
        raise
    finally:
        session.close()


def get_meeting(meeting_id: str) -> Optional[MeetingState]:
    """
    Retrieve meeting by ID.
    
    Args:
        meeting_id: Meeting ID
        
    Returns:
        MeetingState object or None
    """
    session = get_session()
    
    try:
        meeting = session.query(MeetingModel).filter_by(id=meeting_id).first()
        
        if not meeting:
            return None
        
        # Load decisions
        decisions_models = session.query(DecisionModel).filter_by(meeting_id=meeting_id).all()
        decisions = [KeyDecision(**dm.data_json) for dm in decisions_models]
        
        # Load action items
        items_models = session.query(ActionItemModel).filter_by(meeting_id=meeting_id).all()
        action_items = [ActionItem(**im.data_json) for im in items_models]
        
        # Reconstruct MeetingState
        from a2a_protocol.schemas import Utterance
        
        meeting_state = MeetingState(
            id=meeting.id,
            created_at=meeting.created_at,
            input_type=meeting.input_type,
            audio_path=meeting.audio_path,
            transcript_raw=meeting.transcript_raw,
            segments=[Utterance(**seg) for seg in (meeting.segments_json or [])],
            summary=ExecutiveSummary(**meeting.summary_json) if meeting.summary_json else None,
            decisions=decisions,
            action_items=action_items,
            model_used=meeting.model_used,
            processing_time=float(meeting.processing_time) if meeting.processing_time else None
        )
        
        return meeting_state
        
    except Exception as e:
        logger.error(f"Failed to retrieve meeting {meeting_id}: {e}")
        return None
    finally:
        session.close()


def list_meetings(limit: int = 50) -> List[dict]:
    """
    List recent meetings.
    
    Args:
        limit: Maximum number of meetings to return
        
    Returns:
        List of meeting summaries
    """
    session = get_session()
    
    try:
        meetings = session.query(MeetingModel).order_by(
            MeetingModel.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for meeting in meetings:
            result.append({
                "id": meeting.id,
                "created_at": meeting.created_at.isoformat(),
                "input_type": meeting.input_type,
                "transcript_preview": meeting.transcript_raw[:100] + "..." if len(meeting.transcript_raw) > 100 else meeting.transcript_raw,
                "model_used": meeting.model_used
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list meetings: {e}")
        return []
    finally:
        session.close()


# Initialize database on import
init_db()
