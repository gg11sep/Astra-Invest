"""Provider-agnostic LLM client (OpenAI-compatible HTTP)."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Minimal chat completion client.

    Supports OpenAI and any OpenAI-compatible endpoint (Ollama, etc.)
    via environment variables:
      OPENAI_API_KEY
      OPENAI_BASE_URL (default https://api.openai.com/v1)
      OPENAI_MODEL (default gpt-4o-mini)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip(
            "/"
        )
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
    ) -> str:
        if not self.available:
            return ""

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]  # type: ignore[no-any-return]

    async def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        text = await self.chat(system, user + "\n\nRespond with valid JSON only.", temperature)
        if not text:
            return {}
        # Strip markdown fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [ln for ln in lines if not ln.startswith("```")]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            logger.warning("llm_json_parse_failed", preview=cleaned[:200])
            return {"raw_text": cleaned}
