"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

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
    jb_text = Column(Text, nullable=True)