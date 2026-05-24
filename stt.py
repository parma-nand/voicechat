"""
stt.py — Speech to Text using OpenAI Whisper
- Model loaded ONCE at startup
- Tuned for accuracy: base model + better transcription settings
"""

import whisper
import tempfile
import os
import time

_model = None


def get_model(model_size: str = "base"):
    global _model
    if _model is None:
        print(f"[STT] Loading Whisper '{model_size}' model...")
        t = time.time()
        _model = whisper.load_model(model_size)
        print(f"[STT] Model ready in {time.time() - t:.1f}s")
    return _model


def transcribe_bytes(audio_bytes: bytes, model_size: str = "base") -> str:
    """
    Transcribe raw audio bytes to text.
    Tuned settings for better accuracy on lists, names, and short phrases.
    """
    model = get_model(model_size)

    # Save as .webm — matches what browser MediaRecorder sends
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        t = time.time()
        result = model.transcribe(
            tmp_path,
            fp16=False,               # CPU safe — no warning
            language="en",            # skip language detection = faster
            task="transcribe",        # transcribe (not translate)
            temperature=0.0,          # deterministic — no random guessing
            best_of=1,                # no multiple attempts (faster)
            beam_size=5,              # wider search = more accurate
            condition_on_previous_text=False,  # each phrase independent
            no_speech_threshold=0.4,  # lower = picks up quieter speech
            compression_ratio_threshold=2.4,
            initial_prompt="The user is listing items, names, or answering a question clearly.",
        )
        text = result["text"].strip()
        print(f"[STT] Done in {time.time() - t:.1f}s → '{text}'")
        return text
    finally:
        os.unlink(tmp_path)


def transcribe_file(file_path: str, model_size: str = "base") -> str:
    """Transcribe an audio file at a given path."""
    model = get_model(model_size)
    t = time.time()
    result = model.transcribe(
        file_path,
        fp16=False,
        language="en",
        task="transcribe",
        temperature=0.0,
        beam_size=5,
        condition_on_previous_text=False,
        no_speech_threshold=0.4,
        initial_prompt="The user is listing items, names, or answering a question clearly.",
    )
    text = result["text"].strip()
    print(f"[STT] Done in {time.time() - t:.1f}s → '{text}'")
    return text