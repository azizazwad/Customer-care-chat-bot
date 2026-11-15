"""Request bodies accepted by the chat API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MAX_HISTORY_MESSAGES = 20


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="en", pattern="^(en|bn)$")
    # The browser keeps the conversation and sends its recent turns, so the server
    # stores nothing between requests (serverless hosts like Vercel need that).
    history: list[ChatMessage] = Field(default_factory=list, max_length=MAX_HISTORY_MESSAGES)

    def groq_messages(self) -> list[dict[str, str]]:
        """Return the recent history followed by this message, ready to send to Groq."""
        return [turn.model_dump() for turn in self.history] + [
            {"role": "user", "content": self.message.strip()}
        ]
