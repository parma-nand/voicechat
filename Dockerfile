# ── Base image ────────────────────────────────────────────────
FROM python:3.11-slim

# ── System dependencies ────────────────────────────────────────
# ffmpeg   — required by Whisper to decode audio
# build-essential — needed to compile some Python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy source code ───────────────────────────────────────────
COPY . .

# ── Expose port ────────────────────────────────────────────────
EXPOSE 8000

# ── Start FastAPI ──────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]