"""
System status, task list, tunnel info, cookies management.
"""

import os
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import AUDIO_PRESETS, COOKIES_FILE, PORT
from app.manager import manager
from app.tunnel import get_tunnel_url

router = APIRouter(prefix="/api", tags=["system"])
logger = logging.getLogger("ytdlp-api.cookies")


@router.get("/status")
async def system_status():
    tunnel = get_tunnel_url()
    tasks = manager.tasks
    cookies_ok = COOKIES_FILE and os.path.isfile(COOKIES_FILE)
    return {
        "status":       "running",
        "tunnel_url":   tunnel,
        "local_url":    f"http://localhost:{PORT}",
        "download_url": tunnel or f"http://localhost:{PORT}",
        "presets":      list(AUDIO_PRESETS.keys()),
        "cookies":      {
            "loaded":  cookies_ok,
            "path":    COOKIES_FILE,
            "size":    os.path.getsize(COOKIES_FILE) if cookies_ok else 0,
        },
        "tasks": {
            "total":     len(tasks),
            "queued":    sum(
                1 for t in tasks.values() if t.status.value == "queued"
            ),
            "active":    sum(
                1 for t in tasks.values()
                if t.status.value in ("downloading", "processing")
            ),
            "completed": sum(
                1 for t in tasks.values() if t.status.value == "completed"
            ),
            "failed":    sum(
                1 for t in tasks.values() if t.status.value == "failed"
            ),
        },
    }


@router.get("/tasks")
async def list_tasks(limit: int = 50):
    tasks = manager.list_tasks(limit)
    return [
        {
            "task_id":    t.id,
            "type":       t.type.value,
            "status":     t.status.value,
            "progress":   t.progress,
            "title":      t.title,
            "preset":     t.preset,
            "format_id":  t.format_id,
            "filename":   t.filename,
            "file_size":  t.file_size,
            "error":      t.error,
            "created_at": t.created_at,
        }
        for t in tasks
    ]


@router.get("/presets")
async def list_presets():
    return {
        "audio_presets": {
            k: {
                "bitrate":     v["bitrate"],
                "sample_rate": v["sample_rate"],
                "channels":    v["channels"],
            }
            for k, v in AUDIO_PRESETS.items()
        }
    }


# ─── Cookies ──────────────────────────────────────────────

@router.post("/cookies")
async def upload_cookies(file: UploadFile = File(...)):
    """
    Upload a Netscape-format cookies.txt file.
    Export from your browser using an extension like
    'Get cookies.txt LOCALLY' (Chrome) or 'cookies.txt' (Firefox).
    """
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    # Basic validation: Netscape cookie files start with a comment
    text = content.decode("utf-8", errors="replace").strip()
    lines = text.splitlines()
    cookie_lines = [
        l for l in lines
        if l.strip() and not l.strip().startswith("#")
    ]
    if not cookie_lines:
        raise HTTPException(
            400,
            "Invalid cookies.txt format. Must be Netscape format "
            "with at least one cookie line.",
        )

    try:
        cookies_dir = os.path.dirname(COOKIES_FILE)
        if cookies_dir:
            os.makedirs(cookies_dir, exist_ok=True)
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(
            "Cookies uploaded: %d lines -> %s", len(cookie_lines), COOKIES_FILE
        )
    except Exception as exc:
        raise HTTPException(500, f"Failed to save cookies: {exc}")

    return {
        "status":  "ok",
        "message": f"Saved {len(cookie_lines)} cookie lines to {COOKIES_FILE}",
        "path":    COOKIES_FILE,
    }


@router.delete("/cookies")
async def delete_cookies():
    """Remove the cookies file."""
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        os.remove(COOKIES_FILE)
        logger.info("Cookies removed: %s", COOKIES_FILE)
        return {"status": "ok", "message": "Cookies removed"}
    return {"status": "ok", "message": "No cookies file found"}


@router.get("/cookies")
async def cookies_status():
    """Check if cookies are loaded."""
    ok = COOKIES_FILE and os.path.isfile(COOKIES_FILE)
    return {
        "loaded": ok,
        "path":   COOKIES_FILE,
        "size":   os.path.getsize(COOKIES_FILE) if ok else 0,
    }
