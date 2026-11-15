"""Groq's chat completions API: build requests, send them, and read the replies."""

from __future__ import annotations

import http.client
import json
import logging
import re
import time
import urllib.error
import urllib.request
from collections.abc import Iterator

from .config import (
    GROQ_API_URL,
    GROQ_CHAT_MODEL,
    GROQ_MAX_COMPLETION_TOKENS,
    GROQ_NETWORK_RETRIES,
    GROQ_REQUEST_TIMEOUT_SECONDS,
    GROQ_USER_AGENT,
    GROQ_VISION_MODEL,
    read_setting,
)
from .network import ipv4_first_opener
from .prompts import build_system_prompt

logger = logging.getLogger(__name__)


def groq_http_error_detail(exc: urllib.error.HTTPError) -> str:
    """Return a safe, actionable message for an upstream Groq failure."""
    try:
        error_body = exc.read().decode("utf-8", errors="replace")
    except (UnicodeDecodeError, json.JSONDecodeError):
        error_body = ""
    try:
        error_data = json.loads(error_body)
    except json.JSONDecodeError:
        error_data = {}

    error_name = str(error_data.get("error_name", "")).casefold()
    cloudflare_block = (
        error_data.get("error_code") == 1010
        or error_name == "browser_signature_banned"
        or "cloudflare error 1010" in error_body.casefold()
        or "browser_signature_banned" in error_body.casefold()
    )
    cloudflare_ray_id = exc.headers.get("cf-ray") if exc.headers else None
    ray_id = error_data.get("ray_id") or cloudflare_ray_id
    if exc.code == 403 and (cloudflare_block or cloudflare_ray_id):
        logger.error("Groq Cloudflare blocked this client (Error 1010, Ray ID %s)", ray_id)
        detail = (
            "Groq's Cloudflare protection blocked this server request (Error 1010). "
            "This is not an API-key error. Do not retry; contact Groq Support and ask "
            "them to review the blocked client."
        )
        if isinstance(ray_id, str) and re.fullmatch(r"[A-Za-z0-9-]{1,100}", ray_id):
            detail += f" Ray ID: {ray_id}."
        return detail
    if exc.code == 401:
        return "Groq rejected the API key (HTTP 401). Check that the key is active and copied correctly."
    if exc.code == 403:
        error = error_data.get("error", {})
        error_code = error.get("code") if isinstance(error, dict) else None
        if error_code == "model_decommissioned":
            return "Groq no longer serves this model. Choose a model currently listed in your Groq account."
        return "Groq denied this request (HTTP 403). Check the model and account permissions in Groq Console."
    return f"The support service could not complete your request (HTTP {exc.code})."


def build_groq_request(
    prompt: str,
    history: list[dict[str, str]],
    language: str,
    image_data: str | None = None,
    stream: bool = False,
) -> urllib.request.Request:
    """Build a customer-care chat request for Groq without exposing the API key."""
    api_key = read_setting("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("AI support is not configured. Add GROQ_API_KEY to .env.")

    messages: list[dict[str, object]] = [
        {"role": "system", "content": build_system_prompt(language)}
    ]
    messages.extend(history)
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ],
        })
    model = read_setting(
        "GROQ_VISION_MODEL" if image_data else "GROQ_CHAT_MODEL",
        GROQ_VISION_MODEL if image_data else GROQ_CHAT_MODEL,
    )
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_completion_tokens": GROQ_MAX_COMPLETION_TOKENS,
        "stream": stream,
    }).encode("utf-8")
    return urllib.request.Request(
        GROQ_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": GROQ_USER_AGENT,
        },
        method="POST",
    )


def open_groq_response(request: urllib.request.Request) -> http.client.HTTPResponse:
    """Send a Groq request, retrying brief network blips (e.g. a failed DNS lookup)."""
    for attempt in range(GROQ_NETWORK_RETRIES + 1):
        try:
            return ipv4_first_opener.open(request, timeout=GROQ_REQUEST_TIMEOUT_SECONDS)
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, ConnectionError) as exc:
            if attempt == GROQ_NETWORK_RETRIES:
                raise
            logger.warning("Could not reach Groq API (%s); retrying", exc)
            time.sleep(attempt + 1)
    raise AssertionError("unreachable")


def iter_groq_stream(response: http.client.HTTPResponse) -> Iterator[tuple[str, str | None]]:
    """Yield (text, finish_reason) pairs from a streamed Groq chat completion."""
    for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if data == "[DONE]":
            return
        chunk = json.loads(data)
        if "error" in chunk:
            raise ValueError(f"Groq stream error: {chunk['error']}")
        for choice in chunk.get("choices", []):
            yield choice.get("delta", {}).get("content") or "", choice.get("finish_reason")


def request_groq_reply(
    prompt: str,
    history: list[dict[str, str]],
    language: str,
    image_data: str | None = None,
) -> str:
    """Request a complete customer-care response from Groq."""
    request = build_groq_request(prompt, history, language, image_data)
    with open_groq_response(request) as response:
        result = json.loads(response.read().decode("utf-8"))
    choices = result.get("choices", [])
    if not choices or not isinstance(choices[0].get("message", {}).get("content"), str):
        raise ValueError("Groq returned an empty response.")
    answer = choices[0]["message"]["content"].strip()
    if not answer:
        raise ValueError("Groq returned an empty response.")
    return answer
