import os
from contextlib import contextmanager

import numpy as np
from dotenv import load_dotenv

load_dotenv()

_CONN_KWARGS = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "postgresql"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS videos (
    id               SERIAL PRIMARY KEY,
    youtube_url      TEXT UNIQUE NOT NULL,
    title            TEXT,
    channel          TEXT,
    description      TEXT,
    tags             TEXT,
    transcript       TEXT,
    transcript_source TEXT,
    combined_text    TEXT,
    text_embedding   BYTEA,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
"""


def _connect():
    try:
        import psycopg
        return psycopg.connect(**_CONN_KWARGS)
    except ImportError:
        import psycopg2
        return psycopg2.connect(**_CONN_KWARGS)


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _exec(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur


def init_db():
    with get_conn() as conn:
        # Drop and recreate if schema is stale. Remove this line once data is in prod.
        _exec(conn, "DROP TABLE IF EXISTS videos CASCADE;")
        _exec(conn, _CREATE_TABLE)


def url_exists(url: str) -> bool:
    with get_conn() as conn:
        cur = _exec(conn, "SELECT 1 FROM videos WHERE youtube_url = %s", (url,))
        return cur.fetchone() is not None


def insert_video(url: str, info: dict, combined_text: str, text_emb: np.ndarray, visual_emb) -> int | None:
    emb_bytes = text_emb.tobytes() if text_emb is not None else None

    with get_conn() as conn:
        cur = _exec(
            conn,
            """
            INSERT INTO videos
                (youtube_url, title, channel, description, tags,
                 transcript, transcript_source, combined_text, text_embedding)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (youtube_url) DO NOTHING
            RETURNING id
            """,
            (
                url,
                info.get("title"),
                info.get("channel"),
                info.get("description"),
                ",".join(info.get("tags", [])),
                info.get("transcript"),
                info.get("transcript_source"),
                combined_text,
                emb_bytes,
            ),
        )
        row = cur.fetchone()
    return row[0] if row else None


def get_all_videos() -> list[dict]:
    with get_conn() as conn:
        cur = _exec(
            conn,
            "SELECT id, youtube_url, title, channel, description, tags, transcript_source, created_at FROM videos ORDER BY id",
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0], "youtube_url": r[1], "title": r[2],
            "channel": r[3], "description": r[4], "tags": r[5],
            "transcript_source": r[6], "created_at": str(r[7]),
        }
        for r in rows
    ]


def get_all_with_embeddings() -> list[dict]:
    with get_conn() as conn:
        cur = _exec(
            conn,
            "SELECT id, youtube_url, title, channel, transcript_source, text_embedding FROM videos WHERE text_embedding IS NOT NULL ORDER BY id",
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0], "youtube_url": r[1], "title": r[2],
            "channel": r[3], "transcript_source": r[4],
            "embedding": np.frombuffer(r[5], dtype=np.float32),
        }
        for r in rows
    ]


def delete_video(video_id: int) -> bool:
    with get_conn() as conn:
        cur = _exec(conn, "DELETE FROM videos WHERE id = %s RETURNING id", (video_id,))
        return cur.fetchone() is not None
