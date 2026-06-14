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
