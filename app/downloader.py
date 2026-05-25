"""
yt-dlp + FFmpeg wrapper — runs in a thread pool.
Randomized 2026 user-agent rotation + retry logic.
"""

import asyncio
import logging
import os
import random
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import yt_dlp

from app.config import AUDIO_PRESETS, COOKIES_FILE, DOWNLOAD_DIR, DOWNLOAD_TIMEOUT
from app.manager import TaskStatus, TaskType, manager

logger = logging.getLogger("ytdlp-api.dl")


# ─── User-Agent Pool (2026 realistic) ─────────────────────

_UA_POOL: List[str] = [
    # ── Windows ──
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
    # ── Android ──
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/148.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S928B Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/148.0.0.0 Mobile Safari/537.36",
    # ── iPhone / iOS ──
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/148.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    # ── macOS ──
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    # ── Linux ──
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
]


def _pick_ua() -> str:
    return random.choice(_UA_POOL)


# ─── URL Cleaning ─────────────────────────────────────────

# Params that cause playlist/radio/extraction issues
_STRIP_PARAMS = {
    "list", "start_radio", "pp", "t", "time_continue",
    "index", "playnext", "nojs",
}


def _clean_url(url: str) -> str:
    """
    Strip problematic query params from YouTube URLs.
    Keeps only 'v' and other safe params.
    """
    parsed = urlparse(url)
    if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
        return url

    qs = parse_qs(parsed.query, keep_blank_values=True)
    cleaned = {k: v for k, v in qs.items() if k not in _STRIP_PARAMS}

    # youtu.be short URLs — convert to standard
    if "youtu.be" in parsed.netloc and parsed.path.strip("/"):
        cleaned["v"] = [parsed.path.strip("/")]
        new_path = "/watch"
    else:
        new_path = parsed.path

    new_query = urlencode(cleaned, doseq=True)
    cleaned_url = urlunparse((
        parsed.scheme, parsed.netloc, new_path,
        parsed.params, new_query, "",
    ))
    if cleaned_url != url:
        logger.info("Cleaned URL: %s -> %s", url, cleaned_url)
    return cleaned_url


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


def _build_opts(use_cookies: bool = True) -> Dict:
    """
    Build yt-dlp options.
    - Random UA from 2026 pool
    - Cookies when available and requested
    - noplaylist: single video only
    """
    ua = _pick_ua()
    opts: Dict = {
        "quiet":              True,
        "no_warnings":        True,
        "noplaylist":         True,
        "extractor_retries":  3,
        "http_headers": {
            "User-Agent":      ua,
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
        },
    }

    if use_cookies and COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
        logger.info("Cookies ON  UA=%s", ua[0:55])
    else:
        logger.info("Cookies OFF UA=%s", ua[0:55])

    return opts


# ─── Extract with retry ───────────────────────────────────

def _extract_with_retry(url: str, opts: Dict, download: bool = False) -> Dict:
    """
    Try extraction. On failure, retry up to 2 more times:
      1) Same opts (yt-dlp internal retry with different throttle)
      2) Without cookies (in case cookies are stale/causing issues)
    """
    last_err = None
    cleaned = _clean_url(url)

    # Attempt 1: with cookies (if available)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(cleaned, download=download)
    except Exception as e:
        last_err = e
        logger.warning("Attempt 1 failed: %s", e)

    # Attempt 2: fresh UA, same cookie setting
    try:
        opts2 = _build_opts(use_cookies=COOKIES_FILE and os.path.isfile(COOKIES_FILE))
        if "extract_flat" in opts:
            opts2["extract_flat"] = opts["extract_flat"]
        with yt_dlp.YoutubeDL(opts2) as ydl:
            return ydl.extract_info(cleaned, download=download)
    except Exception as e:
        last_err = e
        logger.warning("Attempt 2 failed: %s", e)

    # Attempt 3: NO cookies, fresh UA
    try:
        opts3 = _build_opts(use_cookies=False)
        if "extract_flat" in opts:
            opts3["extract_flat"] = opts["extract_flat"]
        with yt_dlp.YoutubeDL(opts3) as ydl:
            return ydl.extract_info(cleaned, download=download)
    except Exception as e:
        last_err = e
        logger.warning("Attempt 3 failed: %s", e)

    raise last_err


# ─── Info ─────────────────────────────────────────────────

async def get_video_info(url: str) -> Dict:
    loop = asyncio.get_running_loop()

    def _run():
        opts = _build_opts()
        opts["extract_flat"] = False
        info = _extract_with_retry(url, opts, download=False)
        if not info:
            raise ValueError("No info extracted")
        return info

    info = await loop.run_in_executor(None, _run)

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
        opts = _build_opts()
        return _extract_with_retry(url, opts, download=False)

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
            opts = _build_opts()
            opts.update({
                "format":         "bestaudio/best",
                "outtmpl":        outtmpl,
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
            })

            info = _extract_with_retry(task.url, opts, download=True)

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
            opts = _build_opts()
            opts.update({
                "format":              fmt,
                "merge_output_format": "mp4",
                "outtmpl":             outtmpl,
                "progress_hooks":      [_make_hook(task_id)],
                "postprocessors": [
                    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                    {"key": "FFmpegMetadata", "add_metadata": True},
                ],
            })

            info = _extract_with_retry(task.url, opts, download=True)

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
