from fastapi import APIRouter
from app.retrieval.search import search_chunks

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search(query: str):

    results = search_chunks(query)

    return results