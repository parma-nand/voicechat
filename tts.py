"""
tts.py — Text to Speech using gTTS (Google TTS)
- Returns MP3 bytes directly (no temp files)
- Works headlessly in Docker (no audio device needed)
- Falls back to pyttsx3 if gTTS fails (e.g. no internet)
"""

import io
import time
import os


def speak_to_bytes(text: str, lang: str = "en") -> bytes:
    """
    Convert text to MP3 audio bytes.
    Tries gTTS first (better quality), falls back to pyttsx3 (offline).

    Args:
        text : text to convert to speech
        lang : language code (default 'en')
    Returns:
        MP3 audio bytes
    """
    t = time.time()
    try:
        audio_bytes = _gtts(text, lang)
        print(f"[TTS] gTTS done in {time.time() - t:.1f}s ({len(audio_bytes)} bytes)")
        return audio_bytes
    except Exception as e:
        print(f"[TTS] gTTS failed ({e}), falling back to pyttsx3...")
        audio_bytes = _pyttsx3_fallback(text)
        print(f"[TTS] pyttsx3 done in {time.time() - t:.1f}s ({len(audio_bytes)} bytes)")
        return audio_bytes


def _gtts(text: str, lang: str = "en") -> bytes:
    """gTTS — requires internet, high quality."""
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def _pyttsx3_fallback(text: str) -> bytes:
    """
    pyttsx3 offline fallback — saves to temp file, reads back as bytes.
    Works on Windows (SAPI5), Linux (espeak), Mac (NSSpeechSynthesizer).
    """
    import pyttsx3
    import tempfile

    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)


def get_supported_languages() -> dict:
    """Return supported gTTS language codes."""
    from gtts.lang import tts_langs
    return tts_langs()