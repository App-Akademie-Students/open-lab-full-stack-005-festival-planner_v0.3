"""FastAPI app: app object, lifespan (init_db), binds routers.py and static/."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers import router

# Resolved relative to this file, so the app also starts outside the project folder.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class NoCacheStaticFiles(StaticFiles):
    """StaticFiles that makes the browser revalidate every file on each page load.

    Without a Cache-Control header browsers cache app.js/style.css heuristically and may skip
    the request entirely, so after a frontend change the new index.html runs with the old
    app.js. "no-cache" still allows caching, but unchanged files are only confirmed (304).
    """

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.mount("/", NoCacheStaticFiles(directory=STATIC_DIR, html=True), name="static")
