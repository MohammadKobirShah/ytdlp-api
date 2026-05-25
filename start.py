#!/usr/bin/env python3
"""
Entry-point: starts uvicorn.
Tunnel is managed by the FastAPI lifespan in app/main.py.
"""

import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True,
    )
