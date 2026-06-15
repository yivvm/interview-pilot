"""POST /interview - Section 3: likely questions with bullets answer scaffolds."""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db import get_db
from app.models import Analysis, Session
from app.schemas import InterviewResponse
from app.services.llm import LLMClient, LLMError
from app.services.prompts import INTERVIEW_SYSTEM, build_interview_user

router = APIRouter()


class InterviewRequest(BaseModel):
    session_id: str
    jd_text: str | None = None


@router.post("/interview", response_model=InterviewResponse)
async def interview_prep(
    body: InterviewRequest,
    db: DBSession = Depends(get_db),
) -> InterviewResponse:
    session = db.get(Session, body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Optionally accept a new JD from this page; invalidate stale cache if changed.
    if body.jd_text and body.jd_text.strip() and body.jd_text != session.jd_text:
        db.query(Analysis).filter(
            Analysis.session_id == session.id,
            Analysis.kind == "interview",
        ).delete(synchronize_session=False)
        session.jd_text = body.jd_text
        db.commit()

    if not session.jd_text:
        raise HTTPException(
            status_code=400,
            detail="No job description on file. Run the JD Match step first."
        )
    
    cached = (
        db.query(Analysis)
        .filter(Analysis.session_id == session.id, Analysis.kind == "interview")
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if cached is not None:
        payload = json.loads(cached.payload_json)
        return InterviewResponse(**payload, cached=True)
    
    client = LLMClient()
    try:
        result = await client.chat(
            INTERVIEW_SYSTEM,
            build_interview_user(session.resume_text, session.jd_text),
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    
    payload = {"questions": result.get("questions", [])}

    analysis = Analysis(
        session_id=session.id,
        kind="interview",
        payload_json=json.dumps(payload),
        model_name=settings.model_name,
    )
    db.add(analysis)
    db.commit()

    return InterviewResponse(**payload, cached=False)
