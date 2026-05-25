"""
System status, health checks, task list, tunnel info, cookies management.
"""

import os
import logging
import shutil
import subprocess as sp
import time

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import AUDIO_PRESETS, COOKIES_FILE, MIN_DISK_GB, PORT
from app.manager import manager
from app.tunnel import get_tunnel_url

router = APIRouter(prefix="/api", tags=["system"])
logger = logging.getLogger("ytdlp-api.cookies")

_start_time = time.monotonic()


def _check_ffmpeg() -> dict:
    path = shutil.which("ffmpeg")
    if not path:
        return {"status": "not_found", "version": None, "path": None}
    try:
        out = sp.run([path, "-version"], capture_output=True, text=True, timeout=5)
        first = out.stdout.split("\n")[0] if out.stdout else ""
        ver = first.split("version")[-1].split()[0].strip(",") if "version" in first else "unknown"
        return {"status": "ok", "version": ver, "path": path}
    except Exception:
        return {"status": "error", "version": None, "path": path}


def _check_cloudflared() -> dict:
    path = shutil.which("cloudflared")
    if not path:
        return {"status": "not_found", "version": None, "path": None}
    try:
        out = sp.run([path, "--version"], capture_output=True, text=True, timeout=5)
        ver = out.stdout.strip() or out.stderr.strip() or "unknown"
        return {"status": "ok", "version": ver, "path": path}
    except Exception:
        return {"status": "error", "version": None, "path": path}


def _check_disk_space() -> dict:
    from app.config import DOWNLOAD_DIR
    try:
        usage = shutil.disk_usage(os.path.abspath(DOWNLOAD_DIR))
    except Exception:
        usage = shutil.disk_usage(os.path.abspath("."))
    total_gb = usage.total / (1024**3)
    free_gb = usage.free / (1024**3)
    free_pct = (usage.free / usage.total) * 100
    min_gb = max(MIN_DISK_GB, 1)
    if free_gb < min_gb:
        disk_status = "critical"
    elif free_pct < 5:
        disk_status = "critical"
    elif free_pct < 10:
        disk_status = "warning"
    else:
        disk_status = "ok"
    return {
        "status":       disk_status,
        "total_gb":     round(total_gb, 1),
        "used_gb":      round((usage.total - usage.free) / (1024**3), 1),
        "free_gb":      round(free_gb, 1),
        "free_percent": round(free_pct, 1),
    }


def _check_download_dir() -> dict:
    from app.config import DOWNLOAD_DIR
    path = os.path.abspath(DOWNLOAD_DIR)
    exists = os.path.isdir(path)
    writable = os.access(path, os.W_OK) if exists else False
    return {"status": "ok" if (exists and writable) else "error", "path": path, "writable": writable, "exists": exists}


def _check_cookies() -> dict:
    ok = COOKIES_FILE and os.path.isfile(COOKIES_FILE)
    return {
        "loaded": ok,
        "path":   COOKIES_FILE,
        "size":   os.path.getsize(COOKIES_FILE) if ok else 0,
    }


@router.get("/health")
async def system_health():
    """Detailed health check with dependency status."""
    ffmpeg = _check_ffmpeg()
    cloudflared = _check_cloudflared()
    disk = _check_disk_space()
    dldir = _check_download_dir()
    cookies = _check_cookies()
    tunnel = get_tunnel_url()
    tasks = manager.tasks

    # Overall status
    statuses = [ffmpeg["status"], cloudflared["status"], disk["status"], dldir["status"]]
    if "critical" in statuses:
        overall = "unhealthy"
    elif any(s in ("warning", "not_found", "error") for s in statuses):
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "status":       overall,
        "version":      "1.0.0",
        "uptime_seconds": int(time.monotonic() - _start_time),
        "checks": {
            "ffmpeg":     ffmpeg,
            "cloudflared": cloudflared,
            "disk_space":  disk,
            "download_dir": dldir,
            "cookies":     cookies,
        },
        "tunnel": {
            "url":      tunnel,
            "enabled":  tunnel is not None,
        },
        "tasks": {
            "total":     len(tasks),
            "queued":    sum(1 for t in tasks.values() if t.status.value == "queued"),
            "active":    sum(1 for t in tasks.values() if t.status.value in ("downloading", "processing")),
            "completed": sum(1 for t in tasks.values() if t.status.value == "completed"),
            "failed":    sum(1 for t in tasks.values() if t.status.value == "failed"),
        },
    }


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
            "task_id":       t.id,
            "type":          t.type.value,
            "status":        t.status.value,
            "progress":      t.progress,
            "title":         t.title,
            "preset":        t.preset,
            "format_id":     t.format_id,
            "lang":          t.lang,
            "sub_format":    t.sub_format,
            "filename":      t.filename,
            "file_size":     t.file_size,
            "is_playlist":   t.is_playlist,
            "entries_total": t.entries_total,
            "entries_done":  t.entries_done,
            "error":         t.error,
            "created_at":    t.created_at,
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
        ln for ln in lines
        if ln.strip() and not ln.strip().startswith("#")
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
