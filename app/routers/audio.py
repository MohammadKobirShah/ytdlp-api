"""
Audio download endpoints.
"""

import asyncio
import mimetypes
import re
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

from app.config import AUDIO_PRESETS, PORT
from app.manager import TaskStatus, TaskType, manager
from app.downloader import clean_url, process_audio
from app.tunnel import get_tunnel_url

router = APIRouter(prefix="/api/audio", tags=["audio"])

# ─── URL Validation ───────────────────────────────────────

ALLOWED_URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

BLOCKED_HOSTS = re.compile(
    r"^(localhost|127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.|0\.0\.0\.0)",
    re.IGNORECASE,
)


class AudioRequest(BaseModel):
    url: str
    preset: str = "128k"
    playlist: bool = False

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        from urllib.parse import urlparse

        v = clean_url(v)
        if not ALLOWED_URL_PATTERN.match(v):
            raise ValueError("Invalid URL format")
        parsed = urlparse(v)
        if BLOCKED_HOSTS.match(parsed.hostname or ""):
            raise ValueError("Private/internal URLs are not allowed")
        return v


class AudioResponse(BaseModel):
    task_id: str
    status: str
    preset: str
    message: str


def _make_content_disposition(filename: str) -> str:
    ascii_name = filename.encode("ascii", errors="replace").decode("ascii")
    ascii_name = ascii_name.replace('"', "_").replace("\\", "_")
    utf8_name = quote(filename, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{utf8_name}"


def _media_type_for(path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


@router.post("", response_model=AudioResponse)
async def create_audio(req: AudioRequest):
    """Queue an audio download + transcode job."""
    if req.preset not in AUDIO_PRESETS:
        raise HTTPException(
            400,
            f"Invalid preset '{req.preset}'. "
            f"Choose from: {list(AUDIO_PRESETS.keys())}"
        )

    task = manager.create_task(
        url=req.url,
        task_type=TaskType.AUDIO,
        preset=req.preset,
        is_playlist=req.playlist,
    )

    asyncio.create_task(process_audio(task.id))

    return AudioResponse(
        task_id=task.id,
        status=task.status.value,
        preset=req.preset,
        message="Queued. Poll /api/audio/{task_id}/status for progress.",
    )


@router.get("/{task_id}/status")
async def audio_status(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    base = get_tunnel_url() or f"http://localhost:{PORT}"
    dl_link = None
    if task.status == TaskStatus.COMPLETED:
        dl_link = f"{base}/api/audio/{task_id}/download"

    return {
        "task_id":       task.id,
        "type":          task.type.value,
        "status":        task.status.value,
        "progress":      task.progress,
        "preset":        task.preset,
        "title":         task.title,
        "artist":        task.artist,
        "description":   task.description,
        "thumbnail_url": task.thumbnail_url,
        "duration":      task.duration,
        "file_size":     task.file_size,
        "filename":      task.filename,
        "download_url":  dl_link,
        "error":         task.error,
        "created_at":    task.created_at,
        "completed_at":  task.completed_at,
    }


@router.get("/{task_id}/download")
async def download_audio(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            400, f"Task status is '{task.status.value}', not ready."
        )
    if not task.filepath:
        raise HTTPException(500, "File path missing")

    from pathlib import Path

    p = Path(task.filepath)
    if not p.exists():
        raise HTTPException(410, "File was cleaned up")

    return FileResponse(
        path=str(p),
        filename=task.filename or f"{task_id}.mp3",
        media_type=_media_type_for(p),
        headers={
            "Content-Disposition": _make_content_disposition(
                task.filename or f"{task_id}.mp3"
            ),
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.delete("/{task_id}")
async def delete_audio(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    manager.delete(task_id)
    return {"deleted": task_id}
