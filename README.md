# 🎙️ VoiceChat — Browser-based Voice Chatbot

A full-stack voice chatbot with a ChatGPT-style browser UI. Speak into your browser, get a spoken response back.

---

## 📁 Project Structure

```
voice-chatbot/
├── main.py                 # FastAPI backend + route definitions
├── stt.py                  # Speech-to-Text module (Whisper)
├── tts.py                  # Text-to-Speech module (gTTS)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
└── static/
    └── index.html          # Frontend UI (served by FastAPI)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Backend | FastAPI + Uvicorn |
| STT | OpenAI Whisper (`small` model) |
| TTS | gTTS (Google Text-to-Speech) |
| Audio processing | ffmpeg (installed in Docker) |
| Containerization | Docker + Docker Compose |

---

## 🚀 Run with Docker (recommended)

```bash
# 1. Clone / navigate to the project folder
cd voice-chatbot

# 2. Build and start
docker-compose up --build

# 3. Open browser
http://localhost:8000
```

On first run, Whisper downloads the model (~244MB for `small`). It's cached in a Docker volume so subsequent starts are fast.

---

## 🖥️ Run locally (without Docker)

### Requirements
- Python 3.11+
- ffmpeg installed and in PATH

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000

# Open browser
http://localhost:8000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend HTML |
| `POST` | `/transcribe` | Upload audio → returns transcript text |
| `POST` | `/speak` | Send text → returns MP3 audio stream |
| `POST` | `/chat` | Upload audio → transcript + LLM reply text |
| `GET` | `/health` | Health check |

### Example — transcribe audio:
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@recording.wav"
# {"transcript": "hello how are you"}
```

### Example — text to speech:
```bash
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the server"}' \
  --output speech.mp3
```

---

## 🧠 How the Pipeline Works

```
Browser mic → WebM audio blob
       ↓
POST /transcribe → Whisper STT → transcript text
       ↓
POST /chat → LLM (swap in Claude/GPT here) → reply text
       ↓
POST /speak → gTTS → MP3 audio bytes
       ↓
Browser plays MP3
```

---

## 🔧 Swapping in a Real LLM

In `main.py`, find the `/chat` endpoint and replace the placeholder:

```python
# ── Replace this with your LLM call ──
reply = f"You said: {transcript}. This is where your LLM response goes."

# Example with OpenAI:
# import openai
# response = openai.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": transcript}]
# )
# reply = response.choices[0].message.content

# Example with Anthropic Claude:
# import anthropic
# client = anthropic.Anthropic(api_key="your-key")
# msg = client.messages.create(
#     model="claude-sonnet-4-20250514",
#     max_tokens=1024,
#     messages=[{"role": "user", "content": transcript}]
# )
# reply = msg.content[0].text
```

---

## 🎛️ Configuration

### Change Whisper model size (stt.py):
```python
model = whisper.load_model("small")   # tiny / base / small / medium / large
```

### Change TTS language (tts.py):
```python
speak_to_bytes(text, lang="hi")   # hi=Hindi, en=English, etc.
```

---

## ⚠️ Notes

- **Microphone in browser**: requires HTTPS in production. Localhost works without HTTPS.
- **pyttsx3 not used**: replaced with gTTS which works headlessly in Docker (no audio device needed).
- **Whisper FP16 warning**: harmless on CPU — uses FP32 automatically.
- **Whisper model cache**: stored in a Docker volume (`whisper-cache`) so it survives container restarts.