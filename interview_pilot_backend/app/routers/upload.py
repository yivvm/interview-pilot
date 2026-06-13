"""POST /upload - accept a resume file, extract its texts, create a session."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db import get_db
from app.models import Session
from app.schemas import UploadResponse
from app.services.parser import extract_text

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
) -> UploadResponse:
    data = await file.read()

    # 1. Enforce the size limit from config.
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {settings.max_upload_mb} MB.",
        )
    
    # 2. Extract text; parser raises ValueError on unsupported types.
    try:
        text = extract_text(file.filename, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    # 3. Reject empty / image-only files.
    if not text:
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted. The file may be empty or image-only.",
        )
    
    # 4. Persist the session.
    session = Session(resume_filename=file.filename,resume_text=text)
    db.add(session)
    db.commit()
    db.refresh(session)

    # 5. Return the id + a short preview so the UI can confirm parsing worked.
    return UploadResponse(
        session_id=session.id,
        resume_filename=session.resume_filename,
        resume_preview=text[:500],
    )
