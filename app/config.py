import os
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
TEMP_DIR = DOWNLOAD_DIR / "temp"
DOWNLOAD_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ─── Server ──────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ─── Tunnel ──────────────────────────────────────────────
TUNNEL_ENABLED = os.getenv("TUNNEL_ENABLED", "true").lower() == "true"

# ─── Audio Presets ───────────────────────────────────────
AUDIO_PRESETS = {
    "48k":  {"bitrate": "48k",  "sample_rate": 22050, "channels": 1},
    "64k":  {"bitrate": "64k",  "sample_rate": 22050, "channels": 1},
    "128k": {"bitrate": "128k", "sample_rate": 44100, "channels": 2},
    "320k": {"bitrate": "320k", "sample_rate": 48000, "channels": 2},
}

# ─── Concurrency ─────────────────────────────────────────
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "5"))

# ─── Cleanup ─────────────────────────────────────────────
CLEANUP_HOURS = int(os.getenv("CLEANUP_HOURS", "24"))

# ─── Task Limits ─────────────────────────────────────────
MAX_TASKS_IN_MEMORY = int(os.getenv("MAX_TASKS_IN_MEMORY", "1000"))

# ─── Timeouts ────────────────────────────────────────────
DOWNLOAD_TIMEOUT_SECONDS = int(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "1800"))

# ─── FFmpeg / FFprobe ───────────────────────────────────
FFMPEG_BIN  = os.getenv("FFMPEG_BIN",  "ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")
