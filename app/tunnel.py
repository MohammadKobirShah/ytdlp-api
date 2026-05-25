"""
Cloudflared quick-tunnel manager.
Starts a free tunnel, parses the public URL, exposes it via API.
"""

import logging
import re
import subprocess
import threading
import time
from typing import Optional

from app.config import PORT, TUNNEL_ENABLED

logger = logging.getLogger("ytdlp-api")

_tunnel_url: Optional[str] = None
TUNNEL_TIMEOUT = 60  # seconds


def get_tunnel_url() -> Optional[str]:
    return _tunnel_url


def set_tunnel_url(url: str):
    global _tunnel_url
    _tunnel_url = url
    logger.info("🌐 Tunnel active: %s", url)


def start_tunnel():
    """
    Launch cloudflared in a daemon thread.
    Parses the generated *.trycloudflare.com URL from stderr.
    """
    if not TUNNEL_ENABLED:
        logger.info("Tunnel disabled by config")
        return

    def _worker():
        start = time.time()
        try:
            proc = subprocess.Popen(
                [
                    "cloudflared", "tunnel",
                    "--url", f"http://localhost:{PORT}",
                    "--no-autoupdate",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            for line in proc.stderr:
                if time.time() - start > TUNNEL_TIMEOUT:
                    logger.warning(
                        "Tunnel URL not found within %ds", TUNNEL_TIMEOUT
                    )
                    proc.terminate()
                    return
                match = re.search(
                    r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line
                )
                if match:
                    set_tunnel_url(match.group(0))
                    break
            proc.wait()
        except FileNotFoundError:
            logger.warning("cloudflared not found — tunnel not started")
        except Exception:
            logger.exception("Tunnel error")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
