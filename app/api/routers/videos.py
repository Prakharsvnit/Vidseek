from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Video

router = APIRouter(prefix="/videos", tags=["videos"])


class VideoCreate(BaseModel):
    youtube_url: str
    title: str
    channel: str
    duration: int


@router.post("/")
def create_video(video: VideoCreate, db: Session = Depends(get_db)):

    db_video = Video(
        youtube_url=video.youtube_url,
        title=video.title,
        channel=video.channel,
        duration=video.duration
    )

    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    return db_video