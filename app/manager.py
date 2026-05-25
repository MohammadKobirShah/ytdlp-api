"""
Async-safe download task manager.
Holds all state for queued / active / completed / failed tasks.
"""

import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from app.config import CLEANUP_HOURS, DOWNLOAD_DIR, MAX_TASKS_IN_MEMORY

logger = logging.getLogger("ytdlp-api")


class TaskType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"


class TaskStatus(str, Enum):
    QUEUED      = "queued"
    DOWNLOADING = "downloading"
    PROCESSING  = "processing"
    COMPLETED   = "completed"
    FAILED      = "failed"


@dataclass
class Task:
    id: str
    url: str
    type: TaskType
    preset: Optional[str] = None
    format_id: Optional[str] = None
    status: TaskStatus = TaskStatus.QUEUED
    progress: float = 0.0
    filepath: Optional[str] = None
    filename: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


class DownloadManager:
    def __init__(self, max_concurrent: int = 5):
        self.tasks: Dict[str, Task] = {}
        self._max_concurrent = max_concurrent
        self._sem: Optional[asyncio.Semaphore] = None
        self._lock: Optional[asyncio.Lock] = None
        self._thread_lock = threading.Lock()

    def _ensure_primitives(self):
        """Initialize asyncio primitives lazily within a running loop."""
        if self._sem is None:
            self._sem = asyncio.Semaphore(self._max_concurrent)
        if self._lock is None:
            self._lock = asyncio.Lock()

    # ── CRUD ──────────────────────────────────────────────

    def create_task(
        self,
        url: str,
        task_type: TaskType,
        preset: Optional[str] = None,
        format_id: Optional[str] = None,
    ) -> Task:
        # Evict oldest completed/failed tasks if at capacity
        if len(self.tasks) >= MAX_TASKS_IN_MEMORY:
            evictable = sorted(
                (
                    t for t in self.tasks.values()
                    if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
                ),
                key=lambda t: t.created_at,
            )
            for t in evictable[: len(self.tasks) - MAX_TASKS_IN_MEMORY + 1]:
                self.delete(t.id)

        if len(self.tasks) >= MAX_TASKS_IN_MEMORY:
            raise RuntimeError("Task queue full. Try again later.")

        task_id = uuid.uuid4().hex[:12]
        task = Task(
            id=task_id,
            url=url,
            type=task_type,
            preset=preset,
            format_id=format_id,
        )
        self.tasks[task_id] = task
        logger.info("Task created %s  type=%s  url=%s", task_id, task_type, url)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update(self, task_id: str, **kw):
        t = self.tasks.get(task_id)
        if t:
            with self._thread_lock:
                for k, v in kw.items():
                    setattr(t, k, v)

    def list_tasks(self, limit: int = 100) -> List[Task]:
        tasks = sorted(self.tasks.values(), key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    def delete(self, task_id: str):
        t = self.tasks.pop(task_id, None)
        if t and t.filepath:
            p = Path(t.filepath)
            if p.exists():
                p.unlink(missing_ok=True)
                logger.info("Deleted file %s", p)

    # ── Concurrency ───────────────────────────────────────

    async def acquire(self):
        self._ensure_primitives()
        await self._sem.acquire()

    def release(self):
        if self._sem:
            self._sem.release()

    # ── Cleanup ───────────────────────────────────────────

    async def cleanup(self):
        now = time.time()
        cutoff = now - (CLEANUP_HOURS * 3600)
        to_del = [
            tid for tid, t in self.tasks.items()
            if t.completed_at and t.completed_at < cutoff
        ]
        for tid in to_del:
            self.delete(tid)
        if to_del:
            logger.info("Cleaned up %d old tasks", len(to_del))


# ── Singleton ─────────────────────────────────────────────
manager = DownloadManager()
