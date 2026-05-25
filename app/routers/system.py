"""
System status, task list, tunnel info.
"""

from fastapi import APIRouter

from app.manager import manager
from app.tunnel import get_tunnel_url
from app.config import AUDIO_PRESETS, PORT

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/status")
async def system_status():
    tunnel = get_tunnel_url()
    tasks = manager.tasks
    return {
        "status":       "running",
        "tunnel_url":   tunnel,
        "local_url":    f"http://localhost:{PORT}",
        "download_url": tunnel or f"http://localhost:{PORT}",
        "presets":      list(AUDIO_PRESETS.keys()),
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
