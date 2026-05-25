"""
yt-dlp + FFmpeg wrapper — runs in a thread pool.
"""

import asyncio
import logging
import os
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

import yt_dlp

from app.config import AUDIO_PRESETS, COOKIES_FILE, DOWNLOAD_DIR, DOWNLOAD_TIMEOUT
from app.manager import TaskStatus, TaskType, manager

logger = logging.getLogger("ytdlp-api.dl")


# ─── Helpers ──────────────────────────────────────────────

def _sanitize_filename(name: str) -> str:
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name[:200] or "download"


def _sanitize_metadata(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    s = re.sub(r"[\x00-\x1f]", "", s)
    return s[:500]


def _cookies_args() -> List[str]:
    """Return yt-dlp cookie args if cookies file exists."""
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        logger.info("Using cookies from %s", COOKIES_FILE)
        return ["--cookies", COOKIES_FILE]
    return []


# ─── Info ─────────────────────────────────────────────────

async def get_video_info(url: str) -> Dict:
    loop = asyncio.get_running_loop()

    def _run():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "forcejson": True,
        }
        extra = _cookies_args()
        if extra:
            opts["extra_args"] = extra
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await loop.run_in_executor(None, _run)
    if not info:
        raise ValueError("No info extracted")

    formats = []
    for f in info.get("formats") or []:
        try:
            if not isinstance(f, dict):
                continue
            formats.append({
                "format_id":  str(f.get("format_id", "")),
                "ext":        str(f.get("ext", "")),
                "resolution": str(f.get("height", "") or ""),
                "vcodec":     str(f.get("vcodec", "none")),
                "acodec":     str(f.get("acodec", "none")),
                "tbr":        f.get("tbr"),
                "filesize":   f.get("filesize"),
            })
        except Exception:
            continue

    return {
        "title":       info.get("title", ""),
        "duration":    info.get("duration"),
        "thumbnail":   info.get("thumbnail", ""),
        "artist":      info.get("artist") or info.get("uploader") or info.get("channel", ""),
        "description": (info.get("description") or "")[:500],
        "formats":     formats,
    }


async def get_info_dump(url: str, include_raw: bool = False) -> Dict:
    loop = asyncio.get_running_loop()

    def _run():
        opts = {"quiet": True, "no_warnings": True}
        extra = _cookies_args()
        if extra:
            opts["extra_args"] = extra
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await loop.run_in_executor(None, _run)
    if include_raw:
        return info
    return {
        "title":       info.get("title", ""),
        "duration":    info.get("duration"),
        "thumbnail":   info.get("thumbnail", ""),
        "artist":      info.get("artist") or info.get("uploader") or "",
        "description": (info.get("description") or "")[:500],
        "formats":     info.get("formats", []),
    }


# ─── Progress hook ────────────────────────────────────────

def _make_hook(task_id: str):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done  = d.get("downloaded_bytes") or 0
            pct   = (done / total * 100) if total else 0
            manager.update(task_id, progress=min(pct, 99), status=TaskStatus.DOWNLOADING)
        elif d["status"] == "finished":
            manager.update(task_id, progress=99, status=TaskStatus.PROCESSING)
    return hook


# ─── Audio download ───────────────────────────────────────

async def process_audio(task_id: str):
    task = manager.get(task_id)
    if not task:
        return

    preset = AUDIO_PRESETS.get(task.preset, AUDIO_PRESETS["128k"])
    tmp = Path(DOWNLOAD_DIR) / "temp" / task_id
    tmp.mkdir(parents=True, exist_ok=True)

    try:
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)

        loop = asyncio.get_running_loop()

        def _run():
            outtmpl = str(tmp / "audio.%(ext)s")
            opts = {
                "format":        "bestaudio/best",
                "outtmpl":       outtmpl,
                "quiet":         True,
                "no_warnings":   True,
                "progress_hooks": [_make_hook(task_id)],
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": preset["bitrate"].replace("k", ""),
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    },
                    {
                        "key": "EmbedThumbnail",
                    },
                ],
                "postprocessor_args": {
                    "ExtractAudio": [
                        "-ar", str(preset["sample_rate"]),
                        "-ac", str(preset["channels"]),
                    ],
                },
                "writethumbnail": True,
            }
            extra = _cookies_args()
            if extra:
                opts["extra_args"] = extra

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(task.url, download=True)

            title  = info.get("title", task_id) if info else task_id
            artist = (info.get("artist") or info.get("uploader") or "") if info else ""
            dur    = info.get("duration") if info else None
            thumb  = info.get("thumbnail") if info else ""

            mp3s = list(tmp.glob("*.mp3"))
            if not mp3s:
                raise FileNotFoundError("MP3 not found after processing")

            mp3 = mp3s[0]
            safe_name = _sanitize_filename(title)
            fname = f"{safe_name} [{task.preset}].mp3"
            dest  = Path(DOWNLOAD_DIR) / fname
            shutil.move(str(mp3), str(dest))

            return {
                "title":         title,
                "artist":        artist,
                "duration":      dur,
                "thumbnail_url": thumb,
                "filename":      fname,
                "filepath":      str(dest),
                "file_size":     dest.stat().st_size,
            }

        result = await asyncio.wait_for(
            loop.run_in_executor(None, _run),
            timeout=DOWNLOAD_TIMEOUT,
        )

        manager.update(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            title=result["title"],
            artist=result["artist"],
            duration=result["duration"],
            thumbnail_url=result["thumbnail_url"],
            filename=result["filename"],
            filepath=result["filepath"],
            file_size=result["file_size"],
        )
        logger.info("Audio done %s  -> %s  %sB", task_id, result["filepath"], result["file_size"])

    except Exception as exc:
        logger.error("Audio failed %s: %s", task_id, exc)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ─── Video download ───────────────────────────────────────

async def process_video(task_id: str):
    task = manager.get(task_id)
    if not task:
        return

    tmp = Path(DOWNLOAD_DIR) / "temp" / task_id
    tmp.mkdir(parents=True, exist_ok=True)

    try:
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)

        fmt = f"{task.format_id}+bestaudio/best" if task.format_id else "bestvideo+bestaudio/best"
        loop = asyncio.get_running_loop()

        def _run():
            outtmpl = str(tmp / "video.%(ext)s")
            opts = {
                "format":         fmt,
                "merge_output_format": "mp4",
                "outtmpl":        outtmpl,
                "quiet":          True,
                "no_warnings":    True,
                "progress_hooks": [_make_hook(task_id)],
                "postprocessors": [
                    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                    {"key": "FFmpegMetadata", "add_metadata": True},
                ],
            }
            extra = _cookies_args()
            if extra:
                opts["extra_args"] = extra

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(task.url, download=True)

            title = info.get("title", task_id) if info else task_id
            dur   = info.get("duration") if info else None
            thumb = info.get("thumbnail") if info else ""

            vids = list(tmp.glob("video.*"))
            if not vids:
                raise FileNotFoundError("Video not found after download")

            vid = vids[0]
            safe_name = _sanitize_filename(title)
            ext  = vid.suffix or ".mp4"
            fname = f"{safe_name}{ext}"
            dest  = Path(DOWNLOAD_DIR) / fname
            shutil.move(str(vid), str(dest))

            return {
                "title":         title,
                "duration":      dur,
                "thumbnail_url": thumb,
                "filename":      fname,
                "filepath":      str(dest),
                "file_size":     dest.stat().st_size,
            }

        result = await asyncio.wait_for(
            loop.run_in_executor(None, _run),
            timeout=DOWNLOAD_TIMEOUT,
        )

        manager.update(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            title=result["title"],
            duration=result["duration"],
            thumbnail_url=result["thumbnail_url"],
            filename=result["filename"],
            filepath=result["filepath"],
            file_size=result["file_size"],
        )
        logger.info("Video done %s  -> %s  %sB", task_id, result["filepath"], result["file_size"])

    except Exception as exc:
        logger.error("Video failed %s: %s", task_id, exc)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
