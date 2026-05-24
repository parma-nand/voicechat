"""
main.py — FastAPI Voice Chatbot Backend
LLM: OpenAI GPT-4o mini

Endpoints:
  GET  /             → serves frontend
  POST /transcribe   → audio → transcript text (STT)
  POST /speak        → text → MP3 audio (TTS)
  POST /chat         → audio → transcript + GPT reply
  GET  /health       → health check
"""

import io
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from openai import OpenAI

from stt import get_model, transcribe_bytes
from tts import speak_to_bytes
import config

# ── App setup ─────────────────────────────────
app = FastAPI(title="VoiceChat API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ── OpenAI client (single instance) ───────────
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

# ── Conversation history (in-memory) ──────────
# Keeps last 10 messages for context
conversation_history = []
MAX_HISTORY = 10

SYSTEM_PROMPT = """You are a helpful, friendly voice assistant. 
Keep responses concise and conversational since they will be spoken aloud.
Avoid using bullet points, markdown, or special characters in your responses."""


# ── Pre-load Whisper at startup ────────────────
@app.on_event("startup")
async def startup():
    await run_in_threadpool(get_model, config.WHISPER_MODEL)
    print(f"[APP] Ready — model={config.OPENAI_MODEL} | whisper={config.WHISPER_MODEL}")


# ── GPT-4o mini call ───────────────────────────
def get_llm_reply(transcript: str) -> str:
    """
    Send transcript to GPT-4o mini and return reply.
    Maintains conversation history for context.
    """
    global conversation_history

    # Add user message to history
    conversation_history.append({"role": "user", "content": transcript})

    # Keep history within limit
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]

    response = openai_client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=256,           # short responses = faster TTS
        temperature=0.7,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history
        ]
    )

    reply = response.choices[0].message.content.strip()

    # Add assistant reply to history
    conversation_history.append({"role": "assistant", "content": reply})

    print(f"[LLM] GPT-4o-mini → '{reply[:80]}...'")
    return reply


# ── Pydantic models ────────────────────────────
class SpeakRequest(BaseModel):
    text: str
    lang: str = "en"

class ChatResponse(BaseModel):
    transcript: str
    reply: str


# ── Routes ─────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """STT: audio → transcript text."""
    try:
        audio_bytes = await file.read()
        text = await run_in_threadpool(transcribe_bytes, audio_bytes, config.WHISPER_MODEL)
        return JSONResponse({"transcript": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")


@app.post("/speak")
async def speak(request: SpeakRequest):
    """TTS: text → MP3 audio stream."""
    try:
        audio_bytes = await run_in_threadpool(speak_to_bytes, request.text, request.lang)
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(file: UploadFile = File(...)):
    """Full pipeline: audio → STT → GPT-4o mini → reply."""
    try:
        audio_bytes = await file.read()

        # Step 1 — Transcribe audio
        transcript = await run_in_threadpool(transcribe_bytes, audio_bytes, config.WHISPER_MODEL)
        if not transcript:
            raise HTTPException(status_code=400, detail="No speech detected.")

        # Step 2 — GPT-4o mini reply
        reply = await run_in_threadpool(get_llm_reply, transcript)

        return ChatResponse(transcript=transcript, reply=reply)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear_history():
    """Clear conversation history."""
    global conversation_history
    conversation_history = []
    return {"status": "history cleared"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm": config.OPENAI_MODEL,
        "whisper": config.WHISPER_MODEL,
    }