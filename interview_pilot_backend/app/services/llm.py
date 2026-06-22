"""Ollama LLM client.

A thin wrapper around Ollama's /api/chat endpoint that:
- forces JSON output (formt="json"),
- parses the response string into a Python dict,
- retries once with a stricter remainder if the first reply isn't valid JSON.
"""

import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Raises when the LLM call fails or never returns valid JSON."""

class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.model_name
        self.base_url = settings.ollama_host
        self.timeout = settings.request_timeout

    async def chat(self, system: str, user: str) -> dict:
        """Send a system+user prompt; return the parsed JSON object.
        
        Retries once if the model's first reply isn't valid JSON."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        for attempt in range(2):  # initial try + 1 retry
            content = await self._call(messages)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("LLM returned invalid JSON (attempt %d)", attempt + 1)
                # Feed back the bad reply + a stricter reminder, then retry.
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": "That was not valid JSON. Respond with ONLY a valid JSON object, no prose."
                })
        raise LLMError("Model did not return valid JSON after retry.")
        
    async def _call(self, messages: list[dict], json_mode: bool = True) -> str:
        """Once raw call to Ollama /api/chat; returns the message content string."""
        payload = {
            "model": self.model,
            "messages": messages,
            "format": "json",  # ask Ollama to constrain output to valid JSON
            "stream": False,  # get one complete response, not token-by-token
        }
        if json_mode:
            payload["format"] = "json"   # constrain output to valid JSON
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc
        data = resp.json()
        return data["message"]["content"]
    

    async def chat_messages(self, system: str, messages: list[dict]) -> str:
        """Conversational free-text completion (no JSON mode)."""
        full = [{"role": "system"}, {"content": system}, *messages]
        return await self._call(full, json_mode=False)
    