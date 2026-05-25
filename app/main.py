"""
YTDLP-API  —  FastAPI application entry-point.
"""

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import PORT
from app.tunnel import start_tunnel
from app.manager import manager
from app.routers import audio, video, system, webui, docs

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  →  %(message)s",
)
logger = logging.getLogger("ytdlp-api")


# ─── Lifespan ─────────────────────────────────────────────
async def _cleanup_loop():
    while True:
        await asyncio.sleep(3600)
        await manager.cleanup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    start_tunnel()
    cleanup_task = asyncio.create_task(_cleanup_loop())
    logger.info("⚡ YTDLP-API running on http://localhost:%d", PORT)

    yield

    # ── Shutdown ──
    cleanup_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await cleanup_task
    logger.info("Shutting down…")


# ─── App ──────────────────────────────────────────────────
app = FastAPI(
    title="YTDLP-API",
    description=(
        "🔥 Free • No API key • No login • No rate-limit\n\n"
        "Audio: transcode to MP3 (48k / 64k / 128k / 320k) "
        "with full metadata.\n"
        "Video: full format dump JSON + merge best v+a (no transcode).\n"
        "Downloads served via Cloudflared tunnel for "
        "ISP-cached 10× speed."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# ─── CORS — wide open, no auth ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────
app.include_router(webui.router)
app.include_router(docs.router)
app.include_router(audio.router)
app.include_router(video.router)
app.include_router(system.router)
