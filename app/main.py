from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from app.database import delete_video, get_all_videos, init_db
from app.ingest import ingest_seeds
from app.schemas import IngestResponse, SearchResult, VideoOut
from app.search import semantic_search


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="VidSeek — Telegram Semantic Video Search", lifespan=lifespan)


@app.post("/ingest", response_model=IngestResponse)
def ingest():
    """Read seeds.json and ingest all URLs into the DB."""
    return ingest_seeds()


@app.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(..., description="Natural language query, e.g. 'sad romantic vibe'"),
    top_k: int = Query(3, ge=1, le=20),
):
    """Semantic search across all stored videos. Returns top-k matches."""
    results = semantic_search(q, top_k=top_k)
    if not results:
        return []
    return results


@app.get("/videos", response_model=list[VideoOut])
def list_videos():
    """List all stored videos."""
    return get_all_videos()


@app.delete("/videos/{video_id}")
def remove_video(video_id: int):
    """Delete a video by id."""
    if not delete_video(video_id):
        raise HTTPException(status_code=404, detail="Video not found")
    return {"deleted": video_id}
