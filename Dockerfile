FROM python:3.12-slim-bookworm

# ─── System deps ──────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        unzip \
        ca-certificates \
    && curl -fsSL \
        https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
        -o /usr/local/bin/cloudflared \
    && chmod +x /usr/local/bin/cloudflared \
    && curl -fsSL https://deno.land/install.sh | sh \
    && mv /root/.deno/bin/deno /usr/local/bin/deno \
    && chmod +x /usr/local/bin/deno \
    && apt-get purge -y curl unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# ─── Python deps ──────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── App code ─────────────────────────────────────────────
COPY . .
RUN mkdir -p downloads/temp

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000
ENV TUNNEL_ENABLED=true
ENV MAX_CONCURRENT=5
ENV CLEANUP_HOURS=24
ENV MAX_TASKS_IN_MEMORY=1000
ENV DOWNLOAD_TIMEOUT_SECONDS=1800

CMD ["python", "start.py"]
