"""Paths and settings shared by the website and the desktop assistant."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_DIR / "static"
ENV_FILE = PROJECT_DIR / ".env"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"
GROQ_VISION_MODEL = "qwen/qwen3.8-27b"
GROQ_REQUEST_TIMEOUT_SECONDS = 120
GROQ_NETWORK_RETRIES = 2
# gpt-oss counts its hidden reasoning toward this limit, so leave room for both.
GROQ_MAX_COMPLETION_TOKENS = 2048
# Cloudflare blocks Python's default "Python-urllib" agent (Error 1010).
GROQ_USER_AGENT = "Mikey-Customer-Care/1.0"


def read_setting(name: str, default: str = "") -> str:
    """Read a setting from the environment or a local .env file."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            key, separator, entry = line.strip().partition("=")
            if separator and key.strip() == name:
                return entry.strip().strip("\"'")
    return default
