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


# ─── User-Agent Pool ──────────────────────────────────────

_UA_POOL: List[str] = [
    # Windows — Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    # Windows — Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    # Windows — Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) "
    "Gecko/20100101 Firefox/147.0",
    # Android — Chrome
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    # Android — Pixel
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    # iPhone — Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    # iPhone — Chrome
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/148.0.0.0 Mobile/15E148 Safari/604.1",
    # macOS — Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    # macOS — Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    # Linux — Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    # Linux — Firefox
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) "
    "Gecko/20100101 Firefox/147.0",
]


def _pick_ua() -> str:
    return random.choice(_UA_POOL)


# ─── URL Cleaning ─────────────────────────────────────────

# Params that trigger playlist/radio/extraction issues on YouTube
_STRIP_PARAMS = {
    "list", "start_radio", "pp", "t", "time_continue",
    "index", "playnext", "nojs",
}


def _clean_url(url: str) -> str:
    """
    Strip problematic query params from YouTube URLs.
    Also normalises youtu.be short URLs to youtube.com/watch?v=ID.
    """
    parsed = urlparse(url)
    is_youtube = (
        "youtube.com" in parsed.netloc
        or "youtu.be" in parsed.netloc
    )
    if not is_youtube:
        return url

    qs = parse_qs(parsed.query, keep_blank_values=True)

    # ── youtu.be/VIDEO_ID → youtube.com/watch?v=VIDEO_ID ──
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.strip("/")
        if not video_id:
            return url                          # malformed — leave as-is
        cleaned = {"v": [video_id]}             # start fresh; drop all other params
        new_netloc = "www.youtube.com"
        new_path   = "/watch"
    else:
        cleaned    = {k: v for k, v in qs.items() if k not in _STRIP_PARAMS}
        new_netloc = parsed.netloc
        new_path   = parsed.path

    new_query   = urlencode(cleaned, doseq=True)
    cleaned_url = urlunparse((
        parsed.scheme, new_netloc, new_path,
        parsed.params, new_query, "",
    ))

    if cleaned_url != url:
        logger.info("URL cleaned: %s  →  %s", url, cleaned_url)
    return cleaned_url


# ─── Helpers ──────────────────────────────────────────────

def _sanitize_filename(name: str) -> str:
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name[:200] or "download"


def _has_cookies() -> bool:
    return bool(COOKIES_FILE and os.path.isfile(COOKIES_FILE))


def _build_base_opts(use_cookies: bool = True) -> Dict:
    """
    Build the *base* yt-dlp option dict — no format/output/hook settings.
    Callers merge their own format/outtmpl/postprocessor opts on top.
    """
    ua = _pick_ua()
    opts: Dict = {
        "quiet":             True,
        "no_warnings":       True,
        "noplaylist":        True,
        "extractor_retries": 3,
        "http_headers": {
            "User-Agent":                ua,
            "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":           "en-US,en;q=0.9",
            "Accept-Encoding":           "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
        },
    }

    if use_cookies and _has_cookies():
        opts["cookiefile"] = COOKIES_FILE
        logger.debug("Cookies ON  UA=%.55s", ua)
    else:
        logger.debug("Cookies OFF UA=%.55s", ua)

    return opts


# ─── Extract with retry ───────────────────────────────────

def _extract_with_retry(
    url: str,
    extra_opts: Dict,
    download: bool = False,
) -> Dict:
    """
    Try extraction up to three times with escalating fallbacks:
      1. Cookies (if available) + random UA
      2. Fresh UA + same cookie setting
      3. No cookies + fresh UA

    `extra_opts` (format, outtmpl, postprocessors, hooks …) is merged
    on top of the base opts for every attempt so nothing is lost.
    """
    cleaned   = _clean_url(url)
    last_err: Optional[Exception] = None

    cookie_states = [
        _has_cookies(),   # attempt 1: use cookies if available
        _has_cookies(),   # attempt 2: same — new UA only
        False,            # attempt 3: no cookies
    ]

    for attempt, use_cookies in enumerate(cookie_states, start=1):
        opts = {**_build_base_opts(use_cookies=use_cookies), **extra_opts}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(cleaned, download=download)
            logger.info("Attempt %d succeeded for %s", attempt, cleaned)
            return info
        except Exception as exc:
            last_err = exc
            logger.warning("Attempt %d/%d failed: %s", attempt, len(cookie_states), exc)

    # All attempts exhausted
    raise last_err


# ─── Info endpoints ───────────────────────────────────────

async def get_video_info(url: str) -> Dict:
    loop = asyncio.get_running_loop()

    def _run() -> Dict:
        extra  = {"extract_flat": False}
        info   = _extract_with_retry(url, extra, download=False)
        if not info:
            raise ValueError("No info returned by yt-dlp")
        return info

    info    = await loop.run_in_executor(None, _run)
    formats = []

    for f in info.get("formats") or []:
        if not isinstance(f, dict):
            continue
        formats.append({
            "format_id":  str(f.get("format_id", "")),
            "ext":        str(f.get("ext", "")),
            "resolution": str(f.get("height") or ""),
            "vcodec":     str(f.get("vcodec", "none")),
            "acodec":     str(f.get("acodec", "none")),
            "tbr":        f.get("tbr"),
            "filesize":   f.get("filesize"),
        })

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

    def _run() -> Dict:
        return _extract_with_retry(url, {}, download=False)

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
    def hook(d: Dict) -> None:
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done  = d.get("downloaded_bytes") or 0
            pct   = (done / total * 100) if total else 0
            manager.update(task_id, progress=min(pct, 99), status=TaskStatus.DOWNLOADING)
        elif d["status"] == "finished":
            manager.update(task_id, progress=99, status=TaskStatus.PROCESSING)
    return hook


# ─── Audio download ───────────────────────────────────────

async def process_audio(task_id: str) -> None:
    task = manager.get(task_id)
    if not task:
        return

    preset = AUDIO_PRESETS.get(task.preset, AUDIO_PRESETS["128k"])
    tmp    = Path(DOWNLOAD_DIR) / "temp" / task_id
    tmp.mkdir(parents=True, exist_ok=True)

    try:
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)
        loop = asyncio.get_running_loop()

        def _run() -> Dict:
            outtmpl     = str(tmp / "audio.%(ext)s")
            bitrate_num = preset["bitrate"].replace("k", "")

            extra_opts: Dict = {
                "format":         "bestaudio/best",
                "outtmpl":        outtmpl,
                "progress_hooks": [_make_hook(task_id)],
                "writethumbnail": True,
                "postprocessors": [
                    {
                        "key":              "FFmpegExtractAudio",
                        "preferredcodec":   "mp3",
                        "preferredquality": bitrate_num,
                    },
                    {
                        "key":          "FFmpegMetadata",
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
            }

            info = _extract_with_retry(task.url, extra_opts, download=True)

            title  = (info.get("title")  or task_id) if info else task_id
            artist = (info.get("artist") or info.get("uploader") or "") if info else ""
            dur    = info.get("duration")  if info else None
            thumb  = info.get("thumbnail") if info else ""

            mp3s = list(tmp.glob("*.mp3"))
            if not mp3s:
                raise FileNotFoundError("MP3 not found after processing")

            safe_name = _sanitize_filename(title)
            fname     = f"{safe_name} [{task.preset}].mp3"
            dest      = Path(DOWNLOAD_DIR) / fname
            shutil.move(str(mp3s[0]), str(dest))

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
            **result,
        )
        logger.info("Audio done %s → %s (%d B)", task_id, result["filepath"], result["file_size"])

    except Exception as exc:
        logger.error("Audio failed %s: %s", task_id, exc, exc_info=True)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ─── Video download ───────────────────────────────────────

async def process_video(task_id: str) -> None:
    task = manager.get(task_id)
    if not task:
        return

    tmp = Path(DOWNLOAD_DIR) / "temp" / task_id
    tmp.mkdir(parents=True, exist_ok=True)

    try:
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)

        fmt  = (f"{task.format_id}+bestaudio/best" if task.format_id
                else "bestvideo+bestaudio/best")
        loop = asyncio.get_running_loop()

        def _run() -> Dict:
            outtmpl = str(tmp / "video.%(ext)s")

            extra_opts: Dict = {
                "format":              fmt,
                "merge_output_format": "mp4",
                "outtmpl":             outtmpl,
                "progress_hooks":      [_make_hook(task_id)],
                "postprocessors": [
                    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                    {"key": "FFmpegMetadata",        "add_metadata":  True},
                ],
            }

            info = _extract_with_retry(task.url, extra_opts, download=True)

            title = (info.get("title") or task_id) if info else task_id
            dur   = info.get("duration")  if info else None
            thumb = info.get("thumbnail") if info else ""

            vids = list(tmp.glob("video.*"))
            if not vids:
                raise FileNotFoundError("Video file not found after download")

            safe_name = _sanitize_filename(title)
            ext       = vids[0].suffix or ".mp4"
            fname     = f"{safe_name}{ext}"
            dest      = Path(DOWNLOAD_DIR) / fname
            shutil.move(str(vids[0]), str(dest))

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
            **result,
        )
        logger.info("Video done %s → %s (%d B)", task_id, result["filepath"], result["file_size"])

    except Exception as exc:
        logger.error("Video failed %s: %s", task_id, exc, exc_info=True)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
