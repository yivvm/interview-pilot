"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Session(Base):
    """One upload session: the resume now, the pasted job description later."""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=_new_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    resume_filename = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=True)

class Analysis(Base):
    """A cached LLM result for one section of one session."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    kind = Column(String, nullable=False)   # "review" | "match" | "interview"
    created_at = Column(DateTime, default=datetime.utcnow)
    payload_json = Column(Text, nullable=False)   # the full LLM JSON response, as text
    model_name = Column(String, nullable=False)   # e.g. "llama3.1:8b"
