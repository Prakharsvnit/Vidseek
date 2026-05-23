from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(path="./qdrant_data")

collection_name = "video_chunks"

collections = client.get_collections().collections
existing = [c.name for c in collections]

if collection_name not in existing:

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    print("Collection created")

else:
    print("Collection already exists")

client.close()