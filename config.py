"""
config.py — Central configuration for VoiceChat
Provider locked to OpenAI GPT-4o mini.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ──────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# ── OpenAI ────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Whisper STT ───────────────────────────────
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

# ── TTS ───────────────────────────────────────
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")

# ── App ───────────────────────────────────────
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))


# ── Validation ────────────────────────────────
def validate():
    if not OPENAI_API_KEY:
        print("[CONFIG] ⚠️  WARNING: OPENAI_API_KEY is not set in .env")
    else:
        print(f"[CONFIG] ✅ Provider: {LLM_PROVIDER} | Model: {OPENAI_MODEL} | STT: {WHISPER_MODEL}")

validate()