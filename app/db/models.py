from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    youtube_url = Column(Text, unique=True, nullable=False)
    title = Column(Text)
    channel = Column(Text)
    duration = Column(Integer)

    # relationship
    chunks = relationship("VideoChunk", back_populates="video")


class VideoChunk(Base):
    __tablename__ = "video_chunks"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    chunk_index = Column(Integer)
    timestamp_start = Column(Float)
    timestamp_end = Column(Float)
    transcript_text = Column(Text)
    qdrant_point_id = Column(Text)

    # relationship
    video = relationship("Video", back_populates="chunks")