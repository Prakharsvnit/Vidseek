# 🎬 Vidseek — Personal Video Retrieval Engine

*A semantic search engine for retrieving specific moments from your personal video archive.*

---

# 1. Product Overview

**Vidseek** is a **personal video retrieval system** that allows users to instantly find specific moments from saved videos using **natural language queries**.

Instead of searching entire videos manually, the system:

* extracts **transcripts**
* chunks them into semantic units
* creates **vector embeddings**
* stores them in a vector database
* retrieves relevant segments via **hybrid search**

Users can query things like:

```
"that motivational line about discipline"
"funny scene where the guy falls"
"explanation of binary search from that coding video"
```

The system returns:

* the **relevant video**
* the **exact timestamp**
* the **transcript snippet**

---

# 2. Problem Statement

Many users save videos for future reference (YouTube likes, bookmarks, Telegram links, etc.).

However, retrieving **specific moments** from those videos later is difficult.

Typical problems:

1. Users remember **a sentence**, not the title.
2. YouTube search works across **billions of videos**, not a personal curated set.
3. Users must **scrub through entire videos** to find moments.
4. Titles and descriptions often **do not reflect the actual content**.

Example scenario:

You remember a line:

> "Discipline equals freedom"

But you cannot recall:

* the video title
* the creator
* the timestamp

Manual search becomes frustrating.

---

# 3. Why Not Just Use YouTube Search?

This is a question interviewers will almost certainly ask.

### YouTube Search Optimizes For

* global popularity
* engagement metrics
* ad relevance
* recommendation algorithms

Your use case is different.

### Vidseek Optimizes For

* **personal video corpus**
* **semantic moment retrieval**
* **exact timestamp search**
* **hybrid ranking**

Key differences:

| Feature         | YouTube            | Vidseek             |
| --------------- | ------------------ | -------------------- |
| Corpus size     | Billions of videos | Personal curated set |
| Query type      | Keyword            | Natural language     |
| Retrieval unit  | Entire video       | Timestamp chunks     |
| Ranking         | Engagement         | Semantic similarity  |
| Personalization | Behavioral         | Corpus-specific      |

In short:

> YouTube retrieves videos.
> Vidseek retrieves **moments within videos**.

---

# 4. System Architecture

High-level architecture:

```
             +--------------------+
             |  YouTube Links     |
             +---------+----------+
                       |
                       v
               Ingestion Pipeline
                       |
        +--------------+--------------+
        |                             |
        v                             v
 Transcript Extraction        Metadata Storage
        |
        v
  Text Chunking
        |
        v
 Embedding Generation
        |
        v
Vector Storage (pgvector)
        |
        v
Hybrid Retrieval Engine
        |
        v
Ranking + LLM Response
        |
        v
Frontend UI
```

---

# 5. Technology Stack

Backend API:

* FastAPI

UI Layer:

* Streamlit

Database:

* PostgreSQL
* **pgvector extension** for vector search

Embeddings:

* OpenAI text-embedding-3-small

LLM:

* GPT-4o-mini

Evaluation:

* Ragas

Optional transcription fallback:

* Whisper

---

# 6. Data Ingestion Pipeline

The ingestion pipeline processes YouTube links and prepares them for search.

### Step 1 — Video Input

User provides:

```
YouTube video URL
```

Example:

```
https://youtube.com/watch?v=xyz
```

---

### Step 2 — Transcript Extraction

Two strategies:

**Primary**

Use **YouTube transcript API**.

**Fallback**

Use **Whisper transcription** if transcript unavailable.

---

### Step 3 — Text Chunking

The transcript is split into semantic segments.

Example:

```
Chunk 1: 0:00 - 0:20
Chunk 2: 0:20 - 0:40
Chunk 3: 0:40 - 1:00
```

Each chunk contains:

* transcript text
* video id
* timestamp start
* timestamp end

---

### Step 4 — Embedding Generation

Each chunk is converted into a vector using:

**OpenAI text-embedding-3-small**

Example:

```
"Discipline equals freedom"

→ vector[1536 dimensions]
```

---

### Step 5 — Storage

Chunks stored in:

**PostgreSQL + pgvector**

Schema example:

```
video_chunks

id
video_id
timestamp_start
timestamp_end
transcript_text
embedding_vector
```

---

# 7. Hybrid Retrieval Engine

Hybrid search improves recall and precision.

The system combines:

### 1. Vector Search

Find semantically similar chunks.

Example:

Query:

```
"talk about consistency"
```

Matches:

```
"small habits repeated daily"
```

---

### 2. Keyword Search (BM25)

Traditional text search.

Useful for:

* exact phrases
* names
* specific words

---

### 3. Reciprocal Rank Fusion (RRF)

Results from both searches are merged.

Formula:

```
score = 1 / (k + rank)
```

Advantages:

* stable ranking
* robust to noisy results

---

# 8. Retrieval Workflow

User query:

```
"funny scene where the guy slips"
```

Pipeline:

```
Query
 ↓
Embedding generation
 ↓
Vector search
 ↓
Keyword search
 ↓
Reciprocal Rank Fusion
 ↓
Top chunks selected
 ↓
LLM summarization
```

Output:

```
Video: xyz
Timestamp: 02:14
Transcript: "he slipped on the floor and everyone laughed"
```

---

# 9. Citation System

The system returns **source citations**.

Example output:

```
Video: https://youtube.com/watch?v=xyz

Timestamp: 02:14
Transcript:
"discipline equals freedom"
```

User can click the timestamp:

```
youtube.com/watch?v=xyz&t=134
```

This jumps directly to the moment.

---

# 10. Evaluation System

Retrieval quality is evaluated using:

**RAG evaluation metrics**

via:

Ragas

Metrics include:

### Context Precision

How relevant retrieved chunks are.

### Context Recall

Whether correct chunks are retrieved.

### Faithfulness

Whether the LLM response is grounded in context.

### Answer Relevancy

How well answers match queries.

---

# 11. Repository Structure

Production-style project layout:

```
recall-ai/

src/
   ingestion/
   embeddings/
   retrieval/
   ranking/
   api/
   evaluation/

infra/
   docker/

configs/

notebooks/

ui/
   streamlit_app.py
```

---

# 12. Example Query

User query:

```
"explanation of binary search"
```

Retrieved chunk:

```
Video: DSA Lecture
Timestamp: 05:12

Transcript:
Binary search works by dividing the search space into half each time.
```

---

# 13. Performance Targets

For a dataset of:

```
~1000 videos
~10k chunks
```

Expected latency:

| Step            | Time  |
| --------------- | ----- |
| Embedding query | 200ms |
| Vector search   | 50ms  |
| Keyword search  | 30ms  |
| Ranking         | 10ms  |
| LLM response    | 500ms |

Total:

```
~1 second
```

---

# 14. Scaling Design

Current system handles:

```
1K videos
```

Future scaling strategy:

| Component            | Scaling             |
| -------------------- | ------------------- |
| Vector DB            | Pinecone / Weaviate |
| Embedding generation | Batch processing    |
| API                  | Horizontal scaling  |
| Storage              | Object storage      |

---
# 15. Future Improvements

Potential upgrades:

### 1️⃣ Multimodal Retrieval

Use:

* video frame embeddings
* audio embeddings

---

### 2️⃣ Telegram Integration

Automatically ingest saved links.

---

### 3️⃣ Personalized Ranking

Learn user-specific ranking signals.

---

### 4️⃣ Frame-Level Search

Retrieve **visual scenes**, not just speech.

Built a hybrid semantic search engine for retrieving specific moments from personal video archives using vector embeddings, BM25 retrieval, and RAG pipelines with PostgreSQL + pgvector.