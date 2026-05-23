import uuid
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from app.embeddings.embedder import embed_text
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


# ---------- CONFIG ----------

COLLECTION_NAME = "video_chunks"

qdrant = QdrantClient(path="./qdrant_data")


# ---------- UTILS ----------

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    return url.split("v=")[1]


# ---------- METADATA ----------

def get_video_metadata(url):
    """Fetch title, channel, duration"""

    ydl_opts = {"quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info["title"],
        "channel": info["uploader"],
        "duration": info["duration"]
    }


# ---------- TRANSCRIPT ----------

def get_transcript(video_id):
    """Fetch transcript segments"""

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    segments = []

    for seg in transcript:
        segments.append({
            "text": seg.text,
            "start": seg.start,
            "duration": seg.duration
        })

    return segments


# ---------- CHUNKING ----------

def chunk_transcript(transcript, chunk_size=5):
    """
    Combine subtitle segments into larger chunks
    """

    chunks = []
    current_chunk = []
    start_time = transcript[0]["start"]

    for i, segment in enumerate(transcript):

        current_chunk.append(segment["text"])

        if (i + 1) % chunk_size == 0:

            end_time = segment["start"] + segment["duration"]

            chunks.append({
                "text": " ".join(current_chunk),
                "start": start_time,
                "end": end_time
            })

            current_chunk = []
            start_time = end_time

    # last chunk
    if current_chunk:

        chunks.append({
            "text": " ".join(current_chunk),
            "start": start_time,
            "end": transcript[-1]["start"] + transcript[-1]["duration"]
        })

    return chunks



# ---------- STORE IN QDRANT ----------

def store_chunks(chunks, url, metadata):
    """
    Store chunks as vector points in Qdrant
    """

    points = []

    for chunk in chunks:

        embedding = embed_text(chunk["text"])

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk["text"],
                "start": chunk["start"],
                "end": chunk["end"],
                "video_url": url,
                "title": metadata["title"],
                "channel": metadata["channel"]
            }
        )

        points.append(point)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


# ---------- MAIN PIPELINE ----------

def ingest_video(url):

    print("Fetching metadata...")
    metadata = get_video_metadata(url)

    print("Metadata:", metadata)

    video_id = extract_video_id(url)

    print("Fetching transcript...")
    transcript = get_transcript(video_id)

    print("Transcript segments:", len(transcript))

    print("Chunking transcript...")
    chunks = chunk_transcript(transcript)

    print("Chunks created:", len(chunks))

    print("Generating embeddings + storing vectors...")
    store_chunks(chunks, url, metadata)

    print("Video successfully indexed.")


# ---------- ENTRYPOINT ----------

if __name__ == "__main__":

    url = "https://www.youtube.com/watch?v=O5nskjZ_GoI"

    ingest_video(url)