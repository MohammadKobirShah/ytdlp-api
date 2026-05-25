"""
Video info dump + merge-download endpoints.
"""

import asyncio
import mimetypes
import re
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator

from app.config import PORT
from app.manager import TaskStatus, TaskType, manager
from app.downloader import get_info_dump, process_video
from app.tunnel import get_tunnel_url

router = APIRouter(prefix="/api/video", tags=["video"])

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


class VideoRequest(BaseModel):
    url: str
    format_id: Optional[str] = None
    playlist: bool = False

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        from urllib.parse import urlparse

        if not ALLOWED_URL_PATTERN.match(v):
            raise ValueError("Invalid URL format")
        parsed = urlparse(v)
        if BLOCKED_HOSTS.match(parsed.hostname or ""):
            raise ValueError("Private/internal URLs are not allowed")
        return v


class VideoResponse(BaseModel):
    task_id: str
    status: str
    message: str


def _make_content_disposition(filename: str) -> str:
    ascii_name = filename.encode("ascii", errors="replace").decode("ascii")
    ascii_name = ascii_name.replace('"', "_").replace("\\", "_")
    utf8_name = quote(filename, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{utf8_name}"


def _media_type_for(path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


# ─── INFO DUMP ────────────────────────────────────────────

@router.get("/info")
async def video_info(
    url: str = Query(..., description="Video URL"),
    include_raw: bool = Query(
        False, description="Include full yt-dlp info dict"
    ),
    noplaylist: bool = Query(
        True, description="Set false to allow playlist/channel extraction"
    ),
):
    """
    Full format dump for a URL.
    Returns all available formats as JSON.
    When noplaylist=false, returns playlist/channel entries.
    """
    try:
        data = await get_info_dump(url, include_raw=include_raw, noplaylist=noplaylist)
        return JSONResponse(content=data)
    except Exception as exc:
        return JSONResponse(
            status_code=200,
            content={
                "url": url,
                "error": str(exc)[:500],
                "extraction_warnings": [
                    "Partial extraction failure — some fields may be missing"
                ],
                "title": "",
                "duration": None,
                "thumbnail": "",
                "uploader": "",
                "webpage_url": url,
                "extractor": "",
                "description": "",
                "formats": [],
            },
        )


# ─── MERGE DOWNLOAD ───────────────────────────────────────

@router.post("", response_model=VideoResponse)
async def create_video(req: VideoRequest):
    """Queue a video+audio merge download (no transcode, copy only)."""
    task = manager.create_task(
        url=req.url,
        task_type=TaskType.VIDEO,
        format_id=req.format_id,
        is_playlist=req.playlist,
    )

    asyncio.create_task(process_video(task.id))

    return VideoResponse(
        task_id=task.id,
        status=task.status.value,
        message="Queued. Poll /api/video/{task_id}/status for progress.",
    )


@router.get("/{task_id}/status")
async def video_status(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    base = get_tunnel_url() or f"http://localhost:{PORT}"
    dl_link = None
    if task.status == TaskStatus.COMPLETED:
        dl_link = f"{base}/api/video/{task_id}/download"

    return {
        "task_id":       task.id,
        "type":          task.type.value,
        "status":        task.status.value,
        "progress":      task.progress,
        "format_id":     task.format_id,
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
async def download_video(task_id: str):
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
        filename=task.filename or f"{task_id}{p.suffix}",
        media_type=_media_type_for(p),
        headers={
            "Content-Disposition": _make_content_disposition(
                task.filename or f"{task_id}{p.suffix}"
            ),
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.delete("/{task_id}")
async def delete_video(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    manager.delete(task_id)
    return {"deleted": task_id}
