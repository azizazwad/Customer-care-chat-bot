"""The chat API: site configuration, a complete reply, and a streamed reply."""

from __future__ import annotations

import http.client
import json
import logging
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..config import read_setting
from ..groq_client import (
    build_groq_request,
    iter_groq_stream,
    open_groq_response,
    request_groq_reply,
)
from .errors import groq_errors_as_http
from .schemas import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.get("/config")
def get_config() -> dict[str, str | bool]:
    return {
        "business_name": read_setting("BUSINESS_NAME", "Customer Care"),
        "ready": bool(read_setting("GROQ_API_KEY")),
    }


def start_chat_turn(payload: ChatRequest) -> list[dict[str, str]]:
    """Check that chat is available and return the messages to send to Groq."""
    if not read_setting("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Customer care is not configured yet. Add GROQ_API_KEY to your .env file.",
        )
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="Please enter a message.")
    return payload.groq_messages()


@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    messages = start_chat_turn(payload)
    with groq_errors_as_http():
        answer = request_groq_reply(payload.message.strip(), messages, payload.language)
    return {"reply": answer}


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Stream the reply as newline-delimited JSON events: delta, then done or error."""
    messages = start_chat_turn(payload)
    with groq_errors_as_http():
        upstream = open_groq_response(
            build_groq_request(payload.message.strip(), messages, payload.language, stream=True)
        )

    def events() -> Iterator[str]:
        has_text = False
        finish_reason = None
        try:
            for text, finish in iter_groq_stream(upstream):
                if text:
                    has_text = True
                    yield json.dumps({"type": "delta", "text": text}) + "\n"
                finish_reason = finish or finish_reason
            if not has_text:
                raise ValueError("Groq returned an empty response.")
            yield json.dumps({"type": "done", "finish_reason": finish_reason}) + "\n"
        except (OSError, ValueError, http.client.HTTPException):
            logger.exception("Groq stream was interrupted")
            yield json.dumps({
                "type": "error",
                "detail": "The reply was interrupted. Check your internet connection and try again.",
            }) + "\n"
        finally:
            upstream.close()

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
