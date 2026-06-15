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


class Gap(BaseModel):
    skill: str
    severity: str
    suggestion: str

class Rewrite(BaseModel):
    original: str
    improved: str

class MatchResponse(BaseModel):
    match_score: int
    matching_skills: list[str]
    gaps: list[Gap]
    rewrite_suggestions: list[Rewrite]
    cached: bool = False

