from pydantic import BaseModel


class IngestResponse(BaseModel):
    ingested: int
    skipped: int
    failed: list[dict]


class VideoOut(BaseModel):
    id: int
    youtube_url: str
    title: str | None
    channel: str | None
    description: str | None
    tags: str | None
    transcript_source: str | None
    created_at: str


class SearchResult(BaseModel):
    rank: int
    id: int
    title: str | None
    channel: str | None
    youtube_url: str
    score: float
    transcript_source: str | None
