import numpy as np
from fastembed import TextEmbedding

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    embeddings = list(_get_model().embed(texts))
    return np.array(embeddings, dtype=np.float32)


# CLIP visual embedding — requires torch; returns None until torch is available.
def embed_image(image_path: str):
    return None


def embed_query_clip(query: str):
    return None
