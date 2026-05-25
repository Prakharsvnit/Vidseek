import numpy as np

from app.database import get_all_with_embeddings
from app.embedder import embed_texts


def semantic_search(query: str, top_k: int = 3) -> list[dict]:
    rows = get_all_with_embeddings()
    if not rows:
        return []

    query_vec = embed_texts([query])[0]

    # Stack all embeddings into a matrix and compute cosine similarity.
    # OpenAI embeddings are L2-normalised, so dot product == cosine similarity.
    matrix = np.stack([r["embedding"] for r in rows])  # (N, 1536)
    scores = matrix @ query_vec                          # (N,)

    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "rank": rank + 1,
            "id": rows[i]["id"],
            "title": rows[i]["title"],
            "channel": rows[i]["channel"],
            "youtube_url": rows[i]["youtube_url"],
            "transcript_source": rows[i]["transcript_source"],
            "score": round(float(scores[i]), 4),
        }
        for rank, i in enumerate(top_indices)
    ]
