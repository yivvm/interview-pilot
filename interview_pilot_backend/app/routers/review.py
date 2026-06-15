"""POST /review - Section: analyze a resume on its own merits."""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db import get_db
from app.models import Analysis, Session
from app.schemas import ReviewResponse
from app.services.llm import LLMClient, LLMError
from app.services.prompts import REVIEW_SYSTEM, build_review_user

router = APIRouter()

class ReviewRequest(BaseModel):
    session_id: str


@router.post("/review", response_model=ReviewResponse)
async def review_resume(
    body: ReviewRequest,
    db: DBSession = Depends(get_db),
) -> ReviewResponse:
    # 1. Load the session (404 if the id is unknown).
    session = db.get(Session, body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # 2. Cache hit? Return the stored result without calling the LLM.
    cached = (
        db.query(Analysis)
        .filter(Analysis.session_id == session.id, Analysis.kind == "review")
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if cached is not None:
        payload = json.loads(cached.payload_json)
        return ReviewResponse(**payload, cached=True)
    
    # 3. Cache miss: call the LLM.
    client = LLMClient()
    try: 
        result = await client.chat(REVIEW_SYSTEM, build_review_user(session.resume_text))
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    
    # 4. Keep only the fields we expect (guards against extra keys).
    payload = {
        "strengths": result.get("strengths", []),
        "weaknesses": result.get("weaknesses", []),
        "story_prompts": result.get("story_prompts", []),
    }

    # 5. Cache the result.
    analysis = Analysis(
        session_id=session.id,
        kind="review",
        payload_json=json.dumps(payload),
        model_name=settings.model_name,
    )
    db.add(analysis)
    db.commit()

    return ReviewResponse(**payload, cached=False)
