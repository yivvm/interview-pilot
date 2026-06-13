"""Pydantic request/response models (the shapes the API accepts and returns)."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    resume_filename: str
    resume_preview: str
    