"""FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Then open:
    http://localhost:8000/health  -> JSON health check
    http://localhost:8000/docs    -> auto-generated interactive API docs
"""

import httpx
from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="InterviewPilot API", version="0.1.0")

@app.get("/health")
async def health() -> dict:
    """Liveness check + confirms the local Ollama server is reachable."""
    ollama_reachable = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # /api/tags lists installed models; a 200 means Ollama is up.
            resp = await client.get(f"{settings.ollama_host}/api/tags")
            ollama_reachable = resp.status_code == 200
    except httpx.HTTPError:
        ollama_reachable = False
    
    return {
        "status": "ok",
        "ollama_reachable": ollama_reachable,
        "model": settings.model_name,
    }