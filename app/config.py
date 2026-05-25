"""
Central configuration — all env vars with defaults.
"""

import os

PORT                 = int(os.getenv("PORT", "8000"))
HOST                 = os.getenv("HOST", "0.0.0.0")
TUNNEL_ENABLED       = os.getenv("TUNNEL_ENABLED", "true").lower() == "true"
MAX_CONCURRENT       = int(os.getenv("MAX_CONCURRENT", "5"))
CLEANUP_HOURS        = int(os.getenv("CLEANUP_HOURS", "24"))
MAX_TASKS_IN_MEMORY  = int(os.getenv("MAX_TASKS_IN_MEMORY", "1000"))
DOWNLOAD_TIMEOUT     = int(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "1800"))
DOWNLOAD_DIR         = os.getenv("DOWNLOAD_DIR", "downloads")
COOKIES_FILE         = os.getenv("COOKIES_FILE", "/app/cookies.txt")

AUDIO_PRESETS = {
    "48k":  {"bitrate": "48k",  "sample_rate": 22050, "channels": 1},
    "64k":  {"bitrate": "64k",  "sample_rate": 22050, "channels": 1},
    "128k": {"bitrate": "128k", "sample_rate": 44100, "channels": 2},
    "320k": {"bitrate": "320k", "sample_rate": 48000, "channels": 2},
}
