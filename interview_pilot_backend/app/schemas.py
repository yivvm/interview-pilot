"""Pydantic request/response models (the shapes the API accepts and returns)."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    resume_filename: str
    resume_preview: str


class ReviewResponse(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    story_prompts: list[str]
    cached: bool = False   # True if served from cache, not a fresh LLM call
