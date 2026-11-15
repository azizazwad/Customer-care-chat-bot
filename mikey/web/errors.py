"""Turn Groq request failures into safe HTTP errors for the web client."""

from __future__ import annotations

import json
import logging
import urllib.error
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException

from ..config import GROQ_REQUEST_TIMEOUT_SECONDS
from ..groq_client import groq_http_error_detail

logger = logging.getLogger(__name__)


def _timeout_error() -> HTTPException:
    logger.warning(
        "Groq request timed out after %s seconds",
        GROQ_REQUEST_TIMEOUT_SECONDS,
    )
    return HTTPException(
        status_code=504,
        detail=(
            "Groq took too long to respond. Check your internet connection and try again. "
            f"The request timeout is {GROQ_REQUEST_TIMEOUT_SECONDS} seconds."
        ),
    )


@contextmanager
def groq_errors_as_http() -> Iterator[None]:
    """Translate Groq request failures into safe HTTP errors for the web client."""
    try:
        yield
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise HTTPException(
                status_code=429, detail="Support is busy right now. Please try again shortly."
            ) from exc
        detail = groq_http_error_detail(exc)
        raise HTTPException(
            status_code=502, detail=detail
        ) from exc
    except TimeoutError:
        raise _timeout_error() from None
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise _timeout_error() from None
        logger.exception("Could not reach Groq API")
        raise HTTPException(
            status_code=502,
            detail="Could not reach the support service. Check your internet connection and try again.",
        ) from None
    except ConnectionError:
        logger.exception("Could not reach Groq API")
        raise HTTPException(
            status_code=502,
            detail="Could not reach the support service. Check your internet connection and try again.",
        ) from None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        logger.exception("Groq returned an invalid response")
        raise HTTPException(
            status_code=502, detail="The support service returned an invalid response."
        ) from None
