from fastapi import FastAPI
from app.api.routers import videos, search
from app.db.database import engine, Base

app = FastAPI(title="VidSeek")
app.include_router(videos.router)
app.include_router(search.router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "VidSeek API running"}
