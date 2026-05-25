# 🚀 YTDLP-API

![Python Version](https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-05998b?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

A high-performance, production-ready REST API wrapper for `yt-dlp`. Designed for seamless media extraction, automated transcoding, and effortless remote access via Cloudflare tunnels.

**Developed with ❤️ by [MohammadKobirShah](https://github.com/MohammadKobirShah)**

---

## ✨ Key Features

- 🎧 **Smart Audio Transcoding**: Convert any source to MP3 (48k, 64k, 128k, 320k) with automatic ID3 tagging and thumbnail embedding.
- 🎬 **Video Merging**: Automatically merge the best available video and audio streams into high-quality MP4/MKV files.
- 🌐 **Instant Public Access**: Built-in Cloudflare Quick Tunneling — no port forwarding required.
- 🚦 **Advanced Task Manager**: Async task queuing with concurrency control (Semaphores) and automatic cleanup logic.
- 🔒 **Security First**: SSRF protection, host blocklists, and path traversal validation.
- 🐳 **Containerized**: Fully Dockerized for "one-command" deployment.

---

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python)
- **Engine:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Processor:** [FFmpeg](https://ffmpeg.org/)
- **Tunneling:** [Cloudflared](https://github.com/cloudflare/cloudflared)
- **Containerization:** Docker & Docker Compose

---

## 📂 Project Structure

```text
ytdlp-api/
├── app/
│   ├── routers/        # API Endpoints (Audio, Video, System)
│   ├── config.py       # Environment & Global Constants
│   ├── manager.py      # Async Task State & Concurrency
│   ├── downloader.py   # yt-dlp & FFmpeg Logic
│   └── tunnel.py       # Cloudflared Integration
├── downloads/          # Persistent Media Storage
├── Dockerfile          # Multi-stage System Build
├── docker-compose.yml  # Orchestration Config
└── start.py            # Application Entry-point
```

---

## 🚀 Quick Start

### Option A: Docker (Recommended)
Ensure you have Docker and Docker Compose installed.

```bash
# Clone the repository
git clone https://github.com/MohammadKobirShah/ytdlp-api.git
cd ytdlp-api

# Spin up the containers
docker compose up -d --build
```

### Option B: Bare Metal
Requires Python 3.12+, FFmpeg, and Cloudflared installed on your path.

```bash
pip install -r requirements.txt
python start.py
```

---

## 📡 API Documentation

### 1. Extract Video Info
**GET** `/api/video/info?url=<URL>`  
Returns all available formats, resolutions, and metadata.

### 2. Download Audio
**POST** `/api/audio`  
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "preset": "320k"
}
```

### 3. Check Task Status
**GET** `/api/audio/{task_id}/status`  
Returns progress percentage, file size, and the final download link.

---

## ⚙️ Configuration
The application can be tuned via Environment Variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Internal Server Port |
| `TUNNEL_ENABLED` | `true` | Enable/Disable Cloudflare Tunnel |
| `MAX_CONCURRENT` | `5` | Max simultaneous downloads |
| `CLEANUP_HOURS` | `24` | Hours before deleting completed files |
| `MAX_TASKS_IN_MEMORY` | `1000`| Task history limit |

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

## 👤 Author
**MohammadKobirShah**
- GitHub: [@MohammadKobirShah](https://github.com/MohammadKobirShah)
- Role: Lead Developer / Architect

---
*Developed for performance. Built for developers.*
