"""
Anthropic Claude API wrapper for the Slalom Field Services Intelligence Platform.

Model selection:
    HAIKU_MODEL  — Fast, low-cost model for extraction, parsing, and entity resolution.
    SONNET_MODEL — Higher-quality model for generation, scoring, and complex reasoning.
"""

import json
import logging
import re
import uuid
from typing import Any

import anthropic

logger = logging.getLogger(__name__)

HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"

_MARKDOWN_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


class ClaudeError(Exception):
    """
    Raised when a Claude API call fails.

    Attributes:
        error_id: UUID string for correlating this error across logs.
        status:   HTTP status code if available, else None.
    """

    def __init__(self, message: str, error_id: str, status: int | None = None) -> None:
        """Initialise ClaudeError with a correlation ID for logging."""
        super().__init__(message)
        self.error_id = error_id
        self.status = status


class ClaudeClient:
    """
    Thin async wrapper around the Anthropic Python SDK.

    Provides two main methods:
        complete()      — Returns the raw text response from Claude.
        complete_json() — Strips markdown fences and returns a parsed dict/list.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialise the client with an Anthropic API key.

        Args:
            api_key: Anthropic API key (sk-ant-...).
        """
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        system: str,
        user: str,
        model: str = HAIKU_MODEL,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a single-turn prompt to Claude and return the text response.

        Args:
            system:     System prompt defining Claude's role and rules.
            user:       User message / task prompt.
            model:      Model ID (default: HAIKU_MODEL).
            max_tokens: Maximum tokens in the response.

        Returns:
            Raw text content from the first content block.

        Raises:
            ClaudeError: On any API failure.
        """
        error_id = str(uuid.uuid4())
        try:
            message = await self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = message.content[0].text
            logger.debug(
                "Claude response: model=%s input_tokens=%d output_tokens=%d",
                model,
                message.usage.input_tokens,
                message.usage.output_tokens,
            )
            return text
        except anthropic.APIStatusError as exc:
            logger.error("Claude API error [%s]: status=%d %s", error_id, exc.status_code, exc.message)
            raise ClaudeError(str(exc), error_id=error_id, status=exc.status_code) from exc
        except Exception as exc:
            logger.error("Claude unexpected error [%s]: %s", error_id, exc)
            raise ClaudeError(str(exc), error_id=error_id) from exc

    async def complete_json(
        self,
        system: str,
        user: str,
        model: str = HAIKU_MODEL,
        max_tokens: int = 2048,
    ) -> Any:
        """
        Send a prompt expecting a JSON response; strip markdown fences and parse.

        Always include "Return ONLY valid JSON. No markdown fences. No commentary."
        in your system prompt when using this method.

        Args:
            system:     System prompt.
            user:       User prompt.
            model:      Model ID (default: HAIKU_MODEL).
            max_tokens: Maximum tokens in the response.

        Returns:
            Parsed Python object (dict or list).

        Raises:
            ClaudeError: On API failure.
            ValueError:  If the response cannot be parsed as JSON.
        """
        raw = await self.complete(system=system, user=user, model=model, max_tokens=max_tokens)

        # Strip markdown code fences if present
        fence_match = _MARKDOWN_FENCE_RE.search(raw)
        cleaned = fence_match.group(1).strip() if fence_match else raw.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Claude JSON response: %s\nRaw: %s", exc, cleaned[:300])
            raise ValueError(f"Claude returned invalid JSON: {exc}") from exc
