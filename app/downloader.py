"""
yt-dlp wrapper + FFmpeg transcoding / merging / metadata embedding.
All heavy work runs in a thread executor so the event-loop stays free.
"""

import asyncio
import logging
import re
import shutil
import time
import unicodedata
from pathlib import Path
from typing import Optional

import yt_dlp

from app.config import (
    AUDIO_PRESETS,
    DOWNLOAD_DIR,
    DOWNLOAD_TIMEOUT_SECONDS,
    FFMPEG_BIN,
    TEMP_DIR,
)
from app.manager import TaskStatus, manager

logger = logging.getLogger("ytdlp-api")


# ═══════════════════════════════════════════════════════════
#  INFO  –  full format dump
# ═══════════════════════════════════════════════════════════

async def fetch_info(url: str) -> dict:
    """Return full yt-dlp info dict (all formats)."""

    def run():
        opts = {"quiet": True, "nowarnings": True, "socket_timeout": 30}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return ydl.sanitize_info(info)

    return await asyncio.get_running_loop().run_in_executor(None, run)


def _clean_formats(info: dict) -> list:
    """Return a lightweight format list for clients."""
    fmts = []
    for f in info.get("formats", []):
        if not isinstance(f, dict):
            continue
        try:
            fmts.append({
                "format_id":   f.get("format_id"),
                "ext":         f.get("ext"),
                "resolution":  f.get("resolution") or str(f.get("height", "")),
                "fps":         f.get("fps"),
                "vcodec":      f.get("vcodec", "none"),
                "acodec":      f.get("acodec", "none"),
                "tbr":         f.get("tbr"),
                "vbr":         f.get("vbr"),
                "abr":         f.get("abr"),
                "filesize":    f.get("filesize") or f.get("filesize_approx"),
                "note":        f.get("format_note", ""),
            })
        except Exception as exc:
            logger.debug("Skipping malformed format entry: %s", exc)
    return fmts


async def get_info_dump(url: str, include_raw: bool = False) -> dict:
    info = await fetch_info(url)
    result = {
        "title":       info.get("title"),
        "description": info.get("description"),
        "duration":    info.get("duration"),
        "thumbnail":   info.get("thumbnail"),
        "uploader":    info.get("uploader"),
        "artist":      info.get("artist") or info.get("uploader") or info.get("channel"),
        "tags":        info.get("tags", []),
        "categories":  info.get("categories", []),
        "formats":     _clean_formats(info),
    }
    if include_raw:
        result["raw"] = info
    return result


# ═══════════════════════════════════════════════════════════
#  PROGRESS HOOK
# ═══════════════════════════════════════════════════════════

def _make_hook(task_id: str):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done  = d.get("downloaded_bytes", 0)
            pct   = (done / total * 100) if total else 0
            manager.update(
                task_id,
                progress=round(pct, 1),
                status=TaskStatus.DOWNLOADING,
            )
        elif d["status"] == "finished":
            manager.update(task_id, progress=100)
    return hook


# ═══════════════════════════════════════════════════════════
#  AUDIO  –  download → transcode → embed metadata
# ═══════════════════════════════════════════════════════════

async def process_audio(task_id: str):
    task = manager.get(task_id)
    if not task:
        return

    tmp = TEMP_DIR / task_id

    try:
        await manager.acquire()
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)

        tmp.mkdir(parents=True, exist_ok=True)

        # ── 1. Download best audio + thumbnail ────────────
        def download():
            opts = {
                "format":          "bestaudio/best",
                "outtmpl":         str(tmp / "src.%(ext)s"),
                "quiet":           True,
                "nowarnings":      True,
                "write_thumbnail": True,
                "socket_timeout":  30,
                "progress_hooks":  [_make_hook(task_id)],
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(task.url, download=True)

        try:
            info = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(None, download),
                timeout=DOWNLOAD_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Download exceeded {DOWNLOAD_TIMEOUT_SECONDS}s timeout"
            )

        title       = info.get("title", "unknown")
        artist      = (
            info.get("artist")
            or info.get("uploader")
            or info.get("channel")
            or "Unknown"
        )
        description = info.get("description") or ""
        thumb_url   = info.get("thumbnail") or ""
        duration    = info.get("duration")

        manager.update(
            task_id,
            title=title,
            artist=artist,
            description=description,
            thumbnail_url=thumb_url,
            duration=duration,
            status=TaskStatus.PROCESSING,
        )

        # ── 2. Locate source file & thumbnail ─────────────
        src_file = _find_file(
            tmp, "src", exclude_ext={".jpg", ".jpeg", ".png", ".webp"}
        )
        thumb_file = _find_file(
            tmp, exclude_name="src", only_ext={".jpg", ".jpeg", ".png", ".webp"}
        )

        if not src_file:
            raise RuntimeError("Downloaded audio file not found")

        out_file = DOWNLOAD_DIR / f"{task_id}.mp3"
        preset   = AUDIO_PRESETS[task.preset]

        # ── 3. Transcode + embed metadata (single FFmpeg pass) ─
        await _transcode_audio_with_metadata(
            src=str(src_file),
            out=str(out_file),
            thumb=str(thumb_file) if thumb_file else None,
            bitrate=preset["bitrate"],
            sample_rate=preset["sample_rate"],
            channels=preset["channels"],
            title=title,
            artist=artist,
            description=description,
        )

        fsize = out_file.stat().st_size if out_file.exists() else 0
        manager.update(
            task_id,
            status=TaskStatus.COMPLETED,
            filepath=str(out_file),
            filename=_sanitize(f"{title} [{task.preset}].mp3"),
            file_size=fsize,
            completed_at=time.time(),
            progress=100,
        )
        logger.info("Audio done %s  → %s  %dB", task_id, out_file, fsize)

    except Exception as exc:
        logger.exception("Audio failed %s", task_id)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        manager.release()


# ═══════════════════════════════════════════════════════════
#  VIDEO  –  download best v+a → merge (copy) → embed meta
# ═══════════════════════════════════════════════════════════

async def process_video(task_id: str):
    task = manager.get(task_id)
    if not task:
        return

    tmp = TEMP_DIR / task_id

    try:
        await manager.acquire()
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)

        tmp.mkdir(parents=True, exist_ok=True)

        fmt = task.format_id or "bestvideo+bestaudio/best"

        def download():
            opts = {
                "format":               fmt,
                "outtmpl":              str(tmp / "src.%(ext)s"),
                "quiet":                True,
                "nowarnings":           True,
                "write_thumbnail":      True,
                "merge_output_format":  "mp4",
                "embed_metadata":       True,
                "embed_thumbnail":      True,
                "socket_timeout":       30,
                "postprocessor_args":   {"ffmpeg": ["-c", "copy"]},
                "progress_hooks":       [_make_hook(task_id)],
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(task.url, download=True)

        try:
            info = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(None, download),
                timeout=DOWNLOAD_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Download exceeded {DOWNLOAD_TIMEOUT_SECONDS}s timeout"
            )

        title       = info.get("title", "unknown")
        thumb_url   = info.get("thumbnail") or ""
        duration    = info.get("duration")
        artist      = (
            info.get("artist")
            or info.get("uploader")
            or info.get("channel")
            or ""
        )
        description = info.get("description") or ""

        manager.update(
            task_id,
            title=title,
            thumbnail_url=thumb_url,
            duration=duration,
            artist=artist,
            description=description,
            status=TaskStatus.PROCESSING,
        )

        # ── Locate merged file ────────────────────────────
        merged = _find_file(tmp, "src", only_ext={".mp4", ".mkv", ".webm"})
        if not merged:
            merged = _find_file(
                tmp, "src", exclude_ext={".jpg", ".jpeg", ".png", ".webp"}
            )
        if not merged:
            raise RuntimeError("Merged video file not found")

        final = DOWNLOAD_DIR / f"{task_id}{merged.suffix}"
        shutil.move(str(merged), str(final))

        fsize = final.stat().st_size if final.exists() else 0
        manager.update(
            task_id,
            status=TaskStatus.COMPLETED,
            filepath=str(final),
            filename=_sanitize(f"{title}{final.suffix}"),
            file_size=fsize,
            completed_at=time.time(),
            progress=100,
        )
        logger.info("Video done %s  → %s  %dB", task_id, final, fsize)

    except Exception as exc:
        logger.exception("Video failed %s", task_id)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        manager.release()


# ═══════════════════════════════════════════════════════════
#  FFmpeg helpers
# ═══════════════════════════════════════════════════════════

def _sanitize_metadata_value(value: str, max_len: int = 1000) -> str:
    """Remove characters that could corrupt FFmpeg metadata args."""
    if not value:
        return ""
    value = value.replace("\n", " ").replace("\r", " ").replace("\x00", "")
    value = value.replace("=", "\\=").replace(";", "\\;")
    return value[:max_len]


async def _transcode_audio_with_metadata(
    src: str,
    out: str,
    thumb: Optional[str],
    bitrate: str,
    sample_rate: int,
    channels: int,
    title: str,
    artist: str,
    description: str,
):
    """
    Single-pass: transcode to MP3 + embed all tags + thumbnail.
    """
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", src,
    ]
    if thumb and Path(thumb).exists():
        cmd += [
            "-i", thumb,
            "-map", "0:a",
            "-map", "1:v",
            "-c:v", "mjpeg",
            "-disposition:v", "attached_pic",
        ]
    else:
        cmd += ["-vn"]

    cmd += [
        "-c:a",           "libmp3lame",
        "-b:a",           bitrate,
        "-ar",            str(sample_rate),
        "-ac",            str(channels),
        "-metadata",      f"title={_sanitize_metadata_value(title)}",
        "-metadata",      f"artist={_sanitize_metadata_value(artist)}",
        "-metadata",      f"album={_sanitize_metadata_value(title)}",
        "-metadata",      f"comment={_sanitize_metadata_value(description, 500)}",
        "-id3v2_version", "3",
        out,
    ]

    logger.debug("FFmpeg cmd: %s", " ".join(cmd))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed ({proc.returncode}): "
            f"{stderr.decode(errors='replace')[-500:]}"
        )


# ═══════════════════════════════════════════════════════════
#  Utility
# ═══════════════════════════════════════════════════════════

def _find_file(
    directory: Path,
    prefix: str = "",
    exclude_name: str = "",
    only_ext: set = None,
    exclude_ext: set = None,
) -> Optional[Path]:
    resolved_dir = directory.resolve()
    for f in sorted(directory.iterdir()):
        if not f.is_file():
            continue
        # Verify file is within expected directory
        try:
            f.resolve().relative_to(resolved_dir)
        except ValueError:
            logger.warning("Skipping file outside expected dir: %s", f)
            continue
        if prefix and not f.name.startswith(prefix):
            continue
        if exclude_name and f.name.startswith(exclude_name):
            continue
        if only_ext and f.suffix.lower() not in only_ext:
            continue
        if exclude_ext and f.suffix.lower() in exclude_ext:
            continue
        return f
    return None


def _sanitize(name: str) -> str:
    """Remove filesystem-unsafe characters, normalize unicode."""
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?\x00-\x1f\x7f]', '', name)
    name = name.strip(". ")
    name = re.sub(r'_{2,}', '_', name)
    if len(name) > 200:
        dot = name.rfind('.')
        if dot > 0:
            stem, ext = name[:dot], name[dot:]
            name = stem[:200 - len(ext)] + ext
        else:
            name = name[:200]
    return name or "download"
