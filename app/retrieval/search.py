from qdrant_client import QdrantClient
from app.embeddings.embedder import embed_text
COLLECTION_NAME = "video_chunks"

qdrant = QdrantClient(path="./qdrant_data")



def search_chunks(query, limit=5):
    """
    Perform semantic search
    """

    query_vector = embed_text(query)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )

    matches = []

    for r in results:

        matches.append({
            "score": r.score,
            "text": r.payload["text"],
            "start": r.payload["start"],
            "end": r.payload["end"],
            "video_url": r.payload["video_url"],
            "title": r.payload["title"],
            "channel": r.payload["channel"]
        })

    return matches


if __name__ == "__main__":

    query = "early computers"

    results = search_chunks(query)

    for r in results:
        print("\nScore:", r["score"])
        print("Video:", r["title"])
        print("Timestamp:", r["start"])
        print("Text:", r["text"])