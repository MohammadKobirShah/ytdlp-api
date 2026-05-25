"""
yt-dlp + FFmpeg wrapper.
Works with any yt-dlp supported site — no YouTube-specific logic.
Runs blocking yt-dlp calls in a thread-pool executor.
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

import yt_dlp

import zipfile

from app.config import (
    AUDIO_PRESETS,
    COOKIES_FILE,
    DEFAULT_SUB_FORMAT,
    DEFAULT_SUB_LANG,
    DOWNLOAD_DIR,
    DOWNLOAD_TIMEOUT,
)
from app.manager import TaskStatus, manager

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) "
    "Gecko/20100101 Firefox/127.0",
    # Android — Chrome
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    # iPhone — Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
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
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) "
    "Gecko/20100101 Firefox/127.0",
]


def _pick_ua() -> str:
    return random.choice(_UA_POOL)


# ─── Helpers ──────────────────────────────────────────────

def _has_cookies() -> bool:
    """True when a cookies file is configured and actually exists on disk."""
    return bool(COOKIES_FILE and os.path.isfile(COOKIES_FILE))


def _sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename, max 200 chars."""
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name[:200] or "download"


# ─── Base opts ────────────────────────────────────────────

def _build_base_opts(use_cookies: bool = True) -> Dict:
    """
    Return the *base* yt-dlp option dict.

    Deliberately contains NO format, outtmpl, postprocessor, or hook
    settings — callers merge those in via extra_opts so that retry
    attempts always carry the full option set.
    """
    ua = _pick_ua()

    opts: Dict = {
        "quiet":             True,
        "no_warnings":       True,
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
        logger.debug("cookies=ON  ua=%.60s", ua)
    else:
        logger.debug("cookies=OFF ua=%.60s", ua)

    return opts


# ─── Retry wrapper ────────────────────────────────────────

def _extract_with_retry(
    url: str,
    extra_opts: Dict,
    download: bool = False,
) -> Dict:
    """
    Call yt-dlp up to three times with escalating fallbacks.

    Attempt 1 — cookies (if available) + random UA
    Attempt 2 — fresh random UA, same cookie setting
    Attempt 3 — no cookies, fresh UA

    `extra_opts` is merged on top of the base opts for *every* attempt
    so that format / outtmpl / postprocessors / hooks are never lost.
    """
    last_err: Optional[Exception] = None

    # cookie policy per attempt
    cookie_states = [_has_cookies(), _has_cookies(), False]

    for attempt, use_cookies in enumerate(cookie_states, start=1):
        opts = {**_build_base_opts(use_cookies=use_cookies), **extra_opts}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=download)
            logger.info("attempt=%d OK  url=%s", attempt, url)
            return info
        except Exception as exc:
            last_err = exc
            logger.warning(
                "attempt=%d/%d FAIL: %s",
                attempt, len(cookie_states), exc,
            )

    raise last_err  # all attempts exhausted


# ─── Info — lightweight summary ───────────────────────────

async def get_video_info(url: str, *, noplaylist: bool = True) -> Dict:
    """
    Return a lightweight summary dict.
    Works for any URL on any yt-dlp supported site.
    When noplaylist=False, playlist/channel data is returned with entries.
    """
    loop = asyncio.get_running_loop()

    def _run() -> Dict:
        extra: Dict = {}
        if noplaylist:
            extra["noplaylist"] = True
        info = _extract_with_retry(url, extra, download=False)
        if not info:
            raise ValueError("yt-dlp returned no data")
        return info

    info = await loop.run_in_executor(None, _run)

    # Playlist detection
    if info.get("_type") == "playlist" or info.get("entries") is not None:
        entries = []
        for entry in (info.get("entries") or []):
            if not entry:
                continue
            entries.append({
                "id":        entry.get("id", ""),
                "title":     entry.get("title", ""),
                "thumbnail": entry.get("thumbnail", ""),
                "duration":  entry.get("duration"),
                "url":       entry.get("webpage_url") or entry.get("url", ""),
                "extractor": entry.get("extractor", ""),
            })
        return {
            "_type":          "playlist",
            "id":             info.get("id", ""),
            "title":          info.get("title", ""),
            "thumbnail":      info.get("thumbnail") or (entries[0]["thumbnail"] if entries else ""),
            "uploader":       info.get("uploader") or info.get("channel", ""),
            "webpage_url":    info.get("webpage_url", url),
            "extractor":      info.get("extractor", ""),
            "playlist_count": info.get("playlist_count") or len(entries),
            "entries":        entries,
            "description":    (info.get("description") or "")[:500],
        }

    formats: List[Dict] = []
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
            "url":        f.get("url", ""),
        })

    return {
        "title":       info.get("title", ""),
        "duration":    info.get("duration"),
        "thumbnail":   info.get("thumbnail", ""),
        "uploader":    info.get("uploader") or info.get("channel", ""),
        "webpage_url": info.get("webpage_url", url),
        "extractor":   info.get("extractor", ""),
        "description": (info.get("description") or "")[:500],
        "formats":     formats,
    }


# ─── Info — full JSON dump ────────────────────────────────

async def get_info_dump(
    url: str,
    *,
    noplaylist: bool = True,
    include_raw: bool = False,
) -> Any:
    """
    Equivalent to `yt-dlp --dump-json <url>`.

    Parameters
    ----------
    url         : Any URL yt-dlp supports.
    noplaylist  : Pass False to allow playlist/channel extraction.
    include_raw : When True the raw yt-dlp info dict is returned
                  unchanged (all fields, including formats[].url).
                  When False a small safe summary is returned.
    """
    loop = asyncio.get_running_loop()

    def _run() -> Any:
        extra: Dict = {}
        if noplaylist:
            extra["noplaylist"] = True
        return _extract_with_retry(url, extra, download=False)

    info = await loop.run_in_executor(None, _run)

    if include_raw:
        return info

    # Playlist detection
    if info.get("_type") == "playlist" or info.get("entries") is not None:
        entries = []
        for entry in (info.get("entries") or []):
            if not entry:
                continue
            entries.append({
                "id":        entry.get("id", ""),
                "title":     entry.get("title", ""),
                "thumbnail": entry.get("thumbnail", ""),
                "duration":  entry.get("duration"),
                "url":       entry.get("webpage_url") or entry.get("url", ""),
                "extractor": entry.get("extractor", ""),
                "uploader":  entry.get("uploader") or entry.get("channel", ""),
            })
        return {
            "_type":          "playlist",
            "id":             info.get("id", ""),
            "title":          info.get("title", ""),
            "thumbnail":      info.get("thumbnail") or (entries[0]["thumbnail"] if entries else ""),
            "webpage_url":    info.get("webpage_url", url),
            "original_url":   info.get("original_url", url),
            "extractor":      info.get("extractor", ""),
            "extractor_key":  info.get("extractor_key", ""),
            "uploader":       info.get("uploader") or info.get("channel", ""),
            "channel":        info.get("channel", ""),
            "channel_url":    info.get("channel_url", ""),
            "playlist_count": info.get("playlist_count") or len(entries),
            "entries":        entries,
            "description":    (info.get("description") or "")[:1000],
        }

    # Safe summary
    formats: List[Dict] = []
    for f in info.get("formats") or []:
        if not isinstance(f, dict):
            continue
        formats.append({
            "format_id":    str(f.get("format_id", "")),
            "format_note":  str(f.get("format_note", "")),
            "ext":          str(f.get("ext", "")),
            "resolution":   f.get("resolution") or str(f.get("height") or ""),
            "fps":          f.get("fps"),
            "vcodec":       str(f.get("vcodec", "none")),
            "acodec":       str(f.get("acodec", "none")),
            "tbr":          f.get("tbr"),
            "abr":          f.get("abr"),
            "vbr":          f.get("vbr"),
            "filesize":     f.get("filesize"),
            "filesize_approx": f.get("filesize_approx"),
            "language":     f.get("language"),
            "quality":      f.get("quality"),
            "has_drm":      f.get("has_drm", False),
        })

    return {
        "id":                info.get("id", ""),
        "title":             info.get("title", ""),
        "webpage_url":       info.get("webpage_url", url),
        "original_url":      info.get("original_url", url),
        "extractor":         info.get("extractor", ""),
        "extractor_key":     info.get("extractor_key", ""),
        "duration":          info.get("duration"),
        "duration_string":   info.get("duration_string", ""),
        "thumbnail":         info.get("thumbnail", ""),
        "thumbnails":        info.get("thumbnails", []),
        "uploader":          info.get("uploader", ""),
        "uploader_id":       info.get("uploader_id", ""),
        "uploader_url":      info.get("uploader_url", ""),
        "channel":           info.get("channel", ""),
        "channel_id":        info.get("channel_id", ""),
        "channel_url":       info.get("channel_url", ""),
        "view_count":        info.get("view_count"),
        "like_count":        info.get("like_count"),
        "comment_count":     info.get("comment_count"),
        "age_limit":         info.get("age_limit"),
        "upload_date":       info.get("upload_date", ""),
        "timestamp":         info.get("timestamp"),
        "description":       info.get("description", ""),
        "tags":              info.get("tags", []),
        "categories":        info.get("categories", []),
        "chapters":          info.get("chapters", []),
        "subtitles":         list(info.get("subtitles", {}).keys()),
        "automatic_captions": list(info.get("automatic_captions", {}).keys()),
        "formats":           formats,
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


# ─── Subtitle download ────────────────────────────────────

async def process_subtitle(task_id: str) -> None:
    task = manager.get(task_id)
    if not task:
        return

    lang = task.lang or DEFAULT_SUB_LANG
    fmt  = task.sub_format or DEFAULT_SUB_FORMAT
    tmp  = Path(DOWNLOAD_DIR) / "temp" / task_id
    tmp.mkdir(parents=True, exist_ok=True)

    try:
        manager.update(task_id, status=TaskStatus.DOWNLOADING, progress=0)
        loop = asyncio.get_running_loop()

        def _run() -> Dict:
            outtmpl = str(tmp / "subs.%(ext)s")

            extra_opts: Dict = {
                "noplaylist":          True,
                "skip_download":       True,
                "writesubtitles":      True,
                "writeautomaticsubs":  True,
                "subtitleslangs":      [lang],
                "subtitlesformat":     fmt,
                "outtmpl":             outtmpl,
                "progress_hooks":      [_make_hook(task_id)],
            }

            info = _extract_with_retry(task.url, extra_opts, download=True)

            title = _sanitize_filename((info.get("title") or task_id) if info else task_id)

            # Find subtitle files
            sub_files = sorted(tmp.glob(f"*.{fmt}"))
            if not sub_files:
                sub_files = sorted(tmp.glob("*.srt")) or sorted(tmp.glob("*.vtt"))
            if not sub_files:
                raise FileNotFoundError(f"No subtitle files found for language '{lang}'")

            if len(sub_files) == 1:
                ext = sub_files[0].suffix
                fname = f"{title}.{lang}{ext}"
                dest = Path(DOWNLOAD_DIR) / fname
                shutil.move(str(sub_files[0]), str(dest))
            else:
                zip_name = f"{title}.{lang}.subs.zip"
                zip_path = Path(DOWNLOAD_DIR) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for sf in sub_files:
                        zf.write(sf, sf.name)
                for sf in sub_files:
                    sf.unlink(missing_ok=True)
                dest = zip_path
                fname = zip_name

            return {
                "title":         title,
                "artist":        "",
                "duration":      info.get("duration") if info else None,
                "thumbnail_url": info.get("thumbnail") if info else "",
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
        logger.info(
            "subtitle done task=%s file=%s size=%d",
            task_id, result["filepath"], result["file_size"],
        )

    except Exception as exc:
        logger.error("subtitle failed task=%s: %s", task_id, exc, exc_info=True)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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

        is_playlist = task.is_playlist
        playlist_tmp = tmp / "pl"
        if is_playlist:
            playlist_tmp.mkdir(parents=True, exist_ok=True)

        def _run() -> Dict:
            outtmpl = str(tmp / "audio.%(ext)s")
            if is_playlist:
                outtmpl = str(playlist_tmp / "%(playlist_title|Playlist)s" / "%(playlist_index)03d - %(title)s.%(ext)s")

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
            if not is_playlist:
                extra_opts["noplaylist"] = True

            info = _extract_with_retry(task.url, extra_opts, download=True)

            if is_playlist:
                playlist_title = _sanitize_filename(info.get("title") or "Playlist") if info else "Playlist"
                pl_dir = playlist_tmp / playlist_title
                mp3s = []
                if pl_dir.exists():
                    mp3s = sorted(pl_dir.glob("*.mp3"))
                if not mp3s:
                    mp3s = list(playlist_tmp.rglob("*.mp3"))
                if not mp3s:
                    raise FileNotFoundError("No MP3 files found for playlist")

                if len(mp3s) == 1:
                    title = (info.get("title") or task_id) if info else task_id
                    safe  = _sanitize_filename(title)
                    fname = f"{safe} [{task.preset}].mp3"
                    dest  = Path(DOWNLOAD_DIR) / fname
                    shutil.move(str(mp3s[0]), str(dest))
                    return {
                        "title":         title,
                        "artist":        info.get("uploader") or info.get("channel") or "" if info else "",
                        "duration":      info.get("duration") if info else None,
                        "thumbnail_url": info.get("thumbnail") if info else "",
                        "filename":      fname,
                        "filepath":      str(dest),
                        "file_size":     dest.stat().st_size,
                    }

                zip_name = f"{playlist_title} [{task.preset}].zip"
                zip_path = Path(DOWNLOAD_DIR) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for mp3 in mp3s:
                        zf.write(mp3, mp3.name)
                for mp3 in mp3s:
                    mp3.unlink(missing_ok=True)

                total_size = zip_path.stat().st_size
                return {
                    "title":         playlist_title,
                    "artist":        info.get("uploader") or info.get("channel") or "" if info else "",
                    "duration":      None,
                    "thumbnail_url": info.get("thumbnail") if info else "",
                    "filename":      zip_name,
                    "filepath":      str(zip_path),
                    "file_size":     total_size,
                }

            title  = (info.get("title")   or task_id) if info else task_id
            artist = (
                info.get("artist") or info.get("uploader") or info.get("channel") or ""
            ) if info else ""
            dur    = info.get("duration")  if info else None
            thumb  = info.get("thumbnail") if info else ""

            mp3s = list(tmp.glob("*.mp3"))
            if not mp3s:
                raise FileNotFoundError("MP3 not found after processing")

            safe  = _sanitize_filename(title)
            fname = f"{safe} [{task.preset}].mp3"
            dest  = Path(DOWNLOAD_DIR) / fname
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
        logger.info(
            "audio done task=%s file=%s size=%d",
            task_id, result["filepath"], result["file_size"],
        )

    except Exception as exc:
        logger.error("audio failed task=%s: %s", task_id, exc, exc_info=True)
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

        fmt  = (
            f"{task.format_id}+bestaudio/best"
            if task.format_id
            else "bestvideo+bestaudio/best"
        )
        loop = asyncio.get_running_loop()

        is_playlist = task.is_playlist
        playlist_tmp = tmp / "pl"
        if is_playlist:
            playlist_tmp.mkdir(parents=True, exist_ok=True)

        def _run() -> Dict:
            outtmpl = str(tmp / "video.%(ext)s")
            if is_playlist:
                outtmpl = str(playlist_tmp / "%(playlist_title|Playlist)s" / "%(playlist_index)03d - %(title)s.%(ext)s")

            extra_opts: Dict = {
                "format":              fmt,
                "merge_output_format": "mp4",
                "outtmpl":             outtmpl,
                "progress_hooks":      [_make_hook(task_id)],
                "postprocessors": [
                    {
                        "key":            "FFmpegVideoConvertor",
                        "preferedformat": "mp4",
                    },
                    {
                        "key":          "FFmpegMetadata",
                        "add_metadata": True,
                    },
                ],
            }
            if not is_playlist:
                extra_opts["noplaylist"] = True

            info = _extract_with_retry(task.url, extra_opts, download=True)

            if is_playlist:
                playlist_title = _sanitize_filename(info.get("title") or "Playlist") if info else "Playlist"
                pl_dir = playlist_tmp / playlist_title
                vids = []
                if pl_dir.exists():
                    vids = sorted(pl_dir.glob("*"))
                if not vids:
                    vids = sorted(playlist_tmp.rglob("*")) if playlist_tmp.exists() else []
                if not vids:
                    vids = list(tmp.glob("video.*"))
                if not vids:
                    raise FileNotFoundError("No video files found for playlist")

                if len(vids) == 1:
                    title = (info.get("title") or task_id) if info else task_id
                    safe  = _sanitize_filename(title)
                    ext   = vids[0].suffix or ".mp4"
                    fname = f"{safe}{ext}"
                    dest  = Path(DOWNLOAD_DIR) / fname
                    shutil.move(str(vids[0]), str(dest))
                    return {
                        "title":         title,
                        "duration":      info.get("duration") if info else None,
                        "thumbnail_url": info.get("thumbnail") if info else "",
                        "filename":      fname,
                        "filepath":      str(dest),
                        "file_size":     dest.stat().st_size,
                    }

                zip_name = f"{playlist_title}.zip"
                zip_path = Path(DOWNLOAD_DIR) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for vid in vids:
                        zf.write(vid, vid.name)
                for vid in vids:
                    vid.unlink(missing_ok=True)

                total_size = zip_path.stat().st_size
                return {
                    "title":         playlist_title,
                    "duration":      None,
                    "thumbnail_url": info.get("thumbnail") if info else "",
                    "filename":      zip_name,
                    "filepath":      str(zip_path),
                    "file_size":     total_size,
                }

            title = (info.get("title") or task_id) if info else task_id
            dur   = info.get("duration")  if info else None
            thumb = info.get("thumbnail") if info else ""

            vids = list(tmp.glob("video.*"))
            if not vids:
                raise FileNotFoundError("Video file not found after download")

            safe  = _sanitize_filename(title)
            ext   = vids[0].suffix or ".mp4"
            fname = f"{safe}{ext}"
            dest  = Path(DOWNLOAD_DIR) / fname
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
        logger.info(
            "video done task=%s file=%s size=%d",
            task_id, result["filepath"], result["file_size"],
        )

    except Exception as exc:
        logger.error("video failed task=%s: %s", task_id, exc, exc_info=True)
        manager.update(task_id, status=TaskStatus.FAILED, error=str(exc)[:500])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
