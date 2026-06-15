"""POST /match - Section 2: compare a resume against a job description."""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db import get_db
from app.models import Analysis, Session
from app.schemas import MatchResponse
from app.services.llm import LLMClient, LLMError
from app.services.prompts import MATCH_SYSTEM, build_match_user

router = APIRouter()


class MatchRequest(BaseModel):
    session_id: str
    jd_text: str


@router.post("/match", response_model=MatchResponse)
async def match_resume(
    body: MatchRequest,
    db: DBSession = Depends(get_db),
) -> MatchResponse:
    session = db.get(Session, body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Save the JD so Section 3 (/interview) can reuse it.
    session.jd_text = body.jd_text
    db.commit()

    # Cache check.
    cached = (
        db.query(Analysis)
        .filter(Analysis.session_id == session.id, Analysis.kind == "match")
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if cached is not None:
        payload = json.loads(cached.payload_json)
        return MatchResponse(**payload, cached=True)
    
    client = LLMClient()
    try: 
        result = await client.chat(
            MATCH_SYSTEM, build_match_user(session.resume_text, body.jd_text)
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    
    payload = {
        "match_score": int(result.get("match_score") or 0),
        "matching_skills": result.get("matching_skills", []),
        "gaps": result.get("gaps", []),
        "rewrite_suggestions": result.get("rewrite_suggestions", []),
    }

    analysis = Analysis(
        session_id=session.id,
        kind="match",
        payload_json=json.dumps(payload),
        model_name=settings.model_name,
    )
    db.add(analysis)
    db.commit()

    return MatchResponse(**payload, cached=False)
