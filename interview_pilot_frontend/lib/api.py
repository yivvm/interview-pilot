"""Thin HTTP client for the InterviewPilot backend."""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()  # read BACKEND_URL from .env if present

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def upload_resume(filename: str, data: bytes, content_type: str) -> str:
    """POST a resume file to the backend /upload endpoint.
    
    Returns the parsed JSON on success. Raises RuntimeError with the 
    backend's error message on failure (e.g. unsupported file type).
    """
    files = {"file": (filename, data, content_type)}
    resp = httpx.post(f"{BACKEND_URL}/upload", files=files, timeout=30.0)
    if resp.status_code != 200:
        # Backend returns {"detail": "..."} for errors.
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)
    return resp.json()


def review_resume_session(session_id: str) -> str:
    """POST to /review and return the analysis JSON.
    
    Uses a long timeout because the first (uncached) call runs the LLM.
    """
    resp = httpx.post(
        f"{BACKEND_URL}/review",
        json={"session_id": session_id},
        timeout=120.0,
    )
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)
    return resp.json()


def match_resume_session(session_id: str, jd_text: str) -> str:
    """POST to /match with the job description; return the analysis JSON."""
    resp = httpx.post(
        f"{BACKEND_URL}/match",
        json={"session_id": session_id, "jd_text": jd_text},
        timeout=120.0
    )
    if resp.status_code != 200:
        try: 
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)
    return resp.json()


def interview_prep_session(session_id: str) -> str:
    """POST to /interview (uses the JD saved on the session); return the JSON."""
    resp = httpx.post(
        f"{BACKEND_URL}/interview",
        json={"session_id": session_id},
        timeout=120.0,
    )
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)
    return resp.json()
