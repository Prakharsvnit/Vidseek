# VidSeek — Telegram Semantic Video Search

Search your saved YouTube videos using vague natural language memory.

> "sad romantic sacrifice vibe" → returns top 3 closest matches from your collection

## How It Works

1. Add YouTube URLs to `seeds.json`
2. Run `POST /ingest` — fetches metadata, captions, thumbnails, generates embeddings
3. Run `GET /search?q=your+query` — returns top 3 semantically closest videos

**Two embeddings per video:**
- **Text** (384-dim): title + description + tags + transcript (sentence-transformers)
- **Visual** (512-dim): thumbnail image (CLIP ViT-B/32)

**Search score** = 0.6 × text_similarity + 0.4 × visual_similarity

## Quick Start

```bash
# 1. Install (CPU-only torch — smaller download)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 2. Copy env and fill in DB creds
cp .env.example .env

# 3. Add your 10 YouTube URLs to seeds.json

# 4. Start server
uvicorn app.main:app --reload

# 5. Ingest videos (one-time, or re-run to add new ones)
curl -X POST http://localhost:8000/ingest

# 6. Search
curl "http://localhost:8000/search?q=painful+self+growth"
```

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ingest` | Ingest all URLs from seeds.json |
| `GET` | `/search?q=...&top_k=3` | Semantic search, returns top-k |
| `GET` | `/videos` | List all stored videos |
| `DELETE` | `/videos/{id}` | Remove a video |

Interactive docs: http://localhost:8000/docs

## Prerequisites

- Python 3.11+
- PostgreSQL running locally with pgvector extension
- No system ffmpeg needed (`imageio-ffmpeg` handles it via pip)

## Enable Whisper (optional)

For videos without YouTube captions (some Shorts), set in `.env`:
```
WHISPER_ENABLED=true
```
This downloads audio and transcribes locally (~1-3 min per video on CPU).

## Phase 2 — Telegram Channels

Coming next: `POST /ingest/telegram` will pull directly from your Telegram channels using Telethon. Requires `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from [my.telegram.org](https://my.telegram.org).
