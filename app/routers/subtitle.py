"""
Subtitle download endpoints.
"""

import asyncio
import mimetypes
import re
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

from app.config import DEFAULT_SUB_FORMAT, DEFAULT_SUB_LANG, PORT, SUBTITLE_FORMATS
from app.manager import TaskStatus, TaskType, manager
from app.downloader import clean_url, process_subtitle
from app.tunnel import get_tunnel_url

router = APIRouter(prefix="/api/subtitle", tags=["subtitle"])

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


class SubtitleRequest(BaseModel):
    url: str
    lang: str = DEFAULT_SUB_LANG
    format: str = DEFAULT_SUB_FORMAT

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

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v.lower() not in SUBTITLE_FORMATS:
            raise ValueError(
                f"Invalid subtitle format '{v}'. "
                f"Choose from: {sorted(SUBTITLE_FORMATS)}"
            )
        return v.lower()


class SubtitleResponse(BaseModel):
    task_id: str
    status: str
    lang: str
    format: str
    message: str


def _make_content_disposition(filename: str) -> str:
    ascii_name = filename.encode("ascii", errors="replace").decode("ascii")
    ascii_name = ascii_name.replace('"', "_").replace("\\", "_")
    utf8_name = quote(filename, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{utf8_name}"


def _media_type_for(path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


@router.post("", response_model=SubtitleResponse)
async def create_subtitle(req: SubtitleRequest):
    """Queue a subtitle download job."""
    task = manager.create_task(
        url=req.url,
        task_type=TaskType.SUBTITLE,
        preset=None,
        lang=req.lang,
        sub_format=req.format,
    )

    asyncio.create_task(process_subtitle(task.id))

    return SubtitleResponse(
        task_id=task.id,
        status=task.status.value,
        lang=req.lang,
        format=req.format,
        message="Queued. Poll /api/subtitle/{task_id}/status for progress.",
    )


@router.get("/{task_id}/status")
async def subtitle_status(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    base = get_tunnel_url() or f"http://localhost:{PORT}"
    dl_link = None
    if task.status == TaskStatus.COMPLETED:
        dl_link = f"{base}/api/subtitle/{task_id}/download"

    return {
        "task_id":       task.id,
        "type":          task.type.value,
        "status":        task.status.value,
        "progress":      task.progress,
        "lang":          task.lang or DEFAULT_SUB_LANG,
        "sub_format":    task.sub_format or DEFAULT_SUB_FORMAT,
        "title":         task.title,
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
async def download_subtitle(task_id: str):
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
        filename=task.filename or f"{task_id}.vtt",
        media_type=_media_type_for(p),
        headers={
            "Content-Disposition": _make_content_disposition(
                task.filename or f"{task_id}.vtt"
            ),
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.delete("/{task_id}")
async def delete_subtitle(task_id: str):
    task = manager.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    manager.delete(task_id)
    return {"deleted": task_id}
