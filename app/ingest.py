import json

from app.database import insert_video, url_exists
from app.embedder import embed_image, embed_texts
from app.fetcher import fetch_video_info


def _build_combined_text(info: dict) -> str:
    parts = []
    if info.get("channel"):
        parts.append(f"[{info['channel']}]")
    if info.get("title"):
        parts.append(info["title"])
    if info.get("description"):
        parts.append(info["description"][:400])
    if info.get("tags"):
        parts.append("Tags: " + ", ".join(info["tags"][:8]))
    if info.get("transcript"):
        parts.append("Transcript: " + info["transcript"][:800])
    return " ".join(parts)


def ingest_seeds(seeds_path: str = "seeds.json") -> dict:
    with open(seeds_path) as f:
        urls: list[str] = json.load(f)["videos"]

    ingested, skipped, failed = 0, 0, []

    for url in urls:
        if url_exists(url):
            print(f"[skip] already stored: {url}")
            skipped += 1
            continue

        print(f"[fetch] {url}")
        try:
            info = fetch_video_info(url)
            print(f"  title={info['title']} | transcript_source={info['transcript_source']}")

            combined_text = _build_combined_text(info)
            text_emb = embed_texts([combined_text])[0]

            visual_emb = None
            if info.get("thumbnail_path"):
                try:
                    visual_emb = embed_image(info["thumbnail_path"])
                except Exception as e:
                    print(f"  [warn] visual embedding failed: {e}")

            insert_video(url, info, combined_text, text_emb, visual_emb)
            print(f"  [ok] stored id saved")
            ingested += 1

        except Exception as e:
            print(f"  [error] {e}")
            failed.append({"url": url, "error": str(e)})

    return {"ingested": ingested, "skipped": skipped, "failed": failed}
