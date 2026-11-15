"""Create the FastAPI app that Vercel (or uvicorn, locally) runs."""

from __future__ import annotations

import mimetypes
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..config import STATIC_DIR
from .routes import router

# Some Windows setups map .js to text/plain, which browsers refuse for ES modules.
mimetypes.add_type("text/javascript", ".js")


class RevalidatedStaticFiles(StaticFiles):
    """Static files the browser re-checks on every load, so local edits show up right away."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


def create_app() -> FastAPI:
    app = FastAPI(title="Mikey Customer Care", version="1.0.0")
    app.include_router(router)

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})

    # On Vercel, a plain StaticFiles mount is promoted to the CDN at build time.
    static_files = StaticFiles if os.getenv("VERCEL") else RevalidatedStaticFiles
    app.mount("/static", static_files(directory=STATIC_DIR), name="static")
    return app


app = create_app()
