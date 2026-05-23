

# 1. What SQLAlchemy Actually Is

Normally, when using a database, you write **SQL queries manually**.

Example SQL:

```sql
INSERT INTO videos (title, channel)
VALUES ('Python Tutorial', 'freeCodeCamp');
```

But in Python, using **SQLAlchemy ORM**, you instead write:

```python
video = Video(title="Python Tutorial", channel="freeCodeCamp")
session.add(video)
session.commit()
```

SQLAlchemy **converts the Python object into SQL automatically**.

So:

```python
video = Video(...)
```

becomes internally:

```sql
INSERT INTO videos ...
```

---

## ORM Concept

ORM = **Object Relational Mapping**

Mapping:

| Python    | Database |
| --------- | -------- |
| Class     | Table    |
| Object    | Row      |
| Attribute | Column   |

Example mapping:

Python class:

```python
class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    title = Column(Text)
```

---

So SQLAlchemy **maps Python objects to database rows**.

---

# 2. What `Base = declarative_base()` Actually Means

This line is extremely important.

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

It **creates a base class for all ORM models**.

Think of it like:

```
Base
 ├── Video
 ├── VideoChunk
 ├── User
 └── Comment
```

Every table class **inherits from Base**.

Example:

```python
class Video(Base):
```

---

## What `Base` Contains Internally

`declarative_base()` creates a class with:

1️⃣ Metadata registry
2️⃣ Table mapping system
3️⃣ ORM mapping engine

Internally:

```python
class Base:
    metadata = MetaData()
```

This `metadata` stores **all table definitions**.

Example metadata content:

```
metadata
 ├── videos table
 └── video_chunks table
```

Later you can create tables using:

```python
Base.metadata.create_all(engine)
```

SQLAlchemy then generates SQL:

```sql
CREATE TABLE videos (...);
CREATE TABLE video_chunks (...);
```

So **Base collects all models automatically**.

---
## Why Base Is Needed

Without `Base`, SQLAlchemy wouldn't know:

* which classes are tables
* how to generate SQL
* which models exist

So `Base` acts like a **registry of models**.

---

# 5. What pgvector Is

**pgvector** is an extension for **PostgreSQL**.

It adds a new data type:

```
vector
```

Example SQL:

```sql
CREATE TABLE items (
    id SERIAL,
    embedding VECTOR(3)
);
```

Example stored row:

```
id | embedding
---------------------------
1  | [0.1, 0.2, 0.3]
```

---

# 6. How pgvector Stores Vectors Internally

Vector = **array of floating numbers**.

Example:

```
[0.12, -0.44, 0.98]
```

Internally stored like:

```
float4[3]
```

Meaning **3 float values**.

Your example:

```
Vector(1536)
```

Means:

```
1536 floats
```

Memory size:

```
1536 × 4 bytes
≈ 6 KB per vector
```

---

# 7. Example Table with Embeddings

SQL table:

```sql
CREATE TABLE video_chunks (
    id SERIAL,
    transcript_text TEXT,
    embedding VECTOR(1536)
);
```

Example row:

```
id | transcript_text | embedding
------------------------------------------------
1  | Python tutorial | [0.22, 0.88, -0.44 ...]
```

---

---

# 11. Vector Indexing (Very Important)

Without index:

```
scan all rows
```

Slow for large datasets.

pgvector supports **vector indexes**.

Example:

```sql
CREATE INDEX ON video_chunks
USING ivfflat (embedding vector_cosine_ops);
```

This makes **similarity search extremely fast**.

Used in:

* AI search engines
* recommendation systems
* RAG systems

---
---

## Example Flow

Transcript:

```
Python is easy to learn.
Lists store multiple values.
Functions organize code.
```

Split:

```
Chunk 1
Chunk 2
Chunk 3
```

Embedding:

```
Chunk1 → vector
Chunk2 → vector
Chunk3 → vector
```

Store in database.

---

# 13. Example Insert

Python:

```python
chunk = VideoChunk(
    transcript_text="Python lists store multiple values",
    embedding=[0.12, 0.33, -0.55, ...]
)

session.add(chunk)
session.commit()
```

SQL generated:

```sql
INSERT INTO video_chunks
(transcript_text, embedding)
VALUES
('Python lists store multiple values',
'[0.12,0.33,-0.55,...]');
```

---

# 14. Example Search

User asks:

```
"how do lists work?"
```

System:

```
convert question → embedding
```

Example:

```
[0.14, 0.35, -0.60]
```

SQL search:

```sql
SELECT transcript_text
FROM video_chunks
ORDER BY embedding <-> '[0.14,0.35,-0.60]'
LIMIT 3;
```

Returns:

```
"Python lists store multiple values"
```


### pgvector

Extension that allows **vector storage and similarity search in PostgreSQL**.

Features:

* vector datatype
* cosine similarity
* euclidean distance
* vector indexing

I’ll explain **pgvector** from absolute beginner level and go deep into **how it works internally**, including **what vectors are, how they are stored, similarity search, indexing, and what IVFFlat means** in **PostgreSQL**. 🚀

---

# 1. Why pgvector Exists

Traditional databases store things like:

```text
numbers
strings
dates
```

Example table:

| id | title           |
| -- | --------------- |
| 1  | Python Tutorial |
| 2  | Cooking Pasta   |

But modern AI systems work with **vectors (embeddings)**.

Example embedding:

```text
[0.12, -0.88, 0.55, 0.02, ...]
```

These numbers represent **meaning of text**.

Example meanings:

```
"dog" → [0.8, 0.1, 0.3]
"cat" → [0.78, 0.12, 0.28]
"car" → [-0.4, 0.7, 0.2]
```

Notice:

```
dog ≈ cat (similar vectors)
dog ≠ car
```

Normal SQL databases cannot search vectors efficiently.

So **pgvector adds vector support to PostgreSQL**.

---

# 2. What pgvector Adds to PostgreSQL

pgvector introduces:

### 1️⃣ New data type

```
vector
```

Example table:

```sql
CREATE TABLE items (
    id SERIAL,
    embedding VECTOR(3)
);
```

This stores a vector with **3 dimensions**.

Example row:

| id | embedding     |
| -- | ------------- |
| 1  | [0.1,0.2,0.3] |

---

### 2️⃣ Vector distance operators

pgvector adds operators to compare vectors.

Example:

```
<->  Euclidean distance
<=>  Cosine distance
<#>  Inner product
```

Example query:

```sql
SELECT *
FROM items
ORDER BY embedding <-> '[0.1,0.2,0.3]'
LIMIT 5;
```

This returns **5 most similar vectors**.

---

# 3. What a Vector Is (Simple Explanation)

A vector is just **a list of numbers**.

Example:

```
[0.12, 0.44, -0.33]
```

If vector size is 3:

```
3-dimensional space
```

If vector size is 1536:

```
1536-dimensional space
```

Embeddings from models like:

* OpenAI Embeddings API

usually produce **1536 numbers**.

Example:

```
"Python programming"
→
[0.022, -0.91, 0.55, ... 1536 values]
```

---

# 4. Where Embeddings Come From

Embeddings are generated by AI models.

Example pipeline:

```
Text
↓
Embedding model
↓
Vector representation
```

Example:

```
Sentence:
"Python is easy to learn"
```

Embedding:

```
[0.32, -0.22, 0.91, ...]
```

These vectors capture **semantic meaning**.

---

# 5. How pgvector Stores Vectors Internally

Inside PostgreSQL, a vector is stored as:

```
float array
```

Example vector:

```
[0.1, 0.2, 0.3]
```

Internally stored as:

```
float4[3]
```

Each float:

```
4 bytes
```

Example size:

```
Vector(1536)
1536 × 4 bytes = ~6 KB
```

So every embedding row uses about **6 KB storage**.

---

# 6. Creating a Table with pgvector

Example:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    text TEXT,
    embedding VECTOR(3)
);
```

Insert data:

```sql
INSERT INTO documents (text, embedding)
VALUES
('I love dogs', '[0.9,0.1,0.3]'),
('Cats are great', '[0.85,0.12,0.28]'),
('Cars are fast', '[-0.3,0.8,0.2]');
```

---

# 7. Similarity Search

Suppose a user searches:

```
"animals"
```

Embedding generated:

```
[0.88,0.11,0.29]
```

Query:

```sql
SELECT text
FROM documents
ORDER BY embedding <-> '[0.88,0.11,0.29]'
LIMIT 2;
```

Result:

```
I love dogs
Cats are great
```

Because vectors are **closest in space**.

---

# 8. How Distance Is Calculated

pgvector supports multiple distance metrics.

---

## 1️⃣ Euclidean Distance

Formula:

```
√((a1-b1)² + (a2-b2)² + ... )
```

Example:

Vector A:

```
[1,2]
```

Vector B:

```
[4,6]
```

Distance:

```
√((1−4)² + (2−6)²)
= √(9 + 16)
= √25
= 5
```

Smaller distance → more similar.

Operator:

```
<->
```

---

## 2️⃣ Cosine Similarity

Measures **angle between vectors**.

Formula:

```
cosθ = (A·B) / (|A||B|)
```

Example meaning:

```
same direction → similarity = 1
orthogonal → similarity = 0
opposite → similarity = -1
```

Operator:

```
<=>
```

Used most often for **text embeddings**.

---

## 3️⃣ Inner Product

Used for **maximum similarity search**.

Operator:

```
<#>
```

---

# 9. The Problem with Large Datasets

Imagine:

```
10 million vectors
```

If we search:

```
ORDER BY embedding <-> query
```

Database must compare **every row**.

This is called:

```
brute force search
```

Slow for large datasets.

Solution:

```
vector index
```

---

# 10. Vector Indexing

pgvector supports:

```
IVFFlat
HNSW
```

We’ll focus on **IVFFlat**.

---

# 11. What IVFFlat Is

IVFFlat means:

```
Inverted File with Flat Vectors
```

It’s a **vector indexing algorithm**.

Goal:

```
speed up similarity search
```

Instead of searching all vectors.

---

# 12. How IVFFlat Works (Conceptually)

Imagine vectors in space:

```
● ● ● ● ● ● ● ● ●
```

Step 1: cluster vectors.

```
Cluster A
● ● ●

Cluster B
● ● ●

Cluster C
● ●
```

Each cluster has a **centroid**.

Example:

```
centroid A
centroid B
centroid C
```

---

Step 2: assign vectors to clusters.

Example:

```
Cluster A → vectors 1,2,3
Cluster B → vectors 4,5,6
Cluster C → vectors 7,8
```

---

Step 3: search process.

User query vector arrives.

System:

```
find closest cluster
```

Example:

```
query → cluster B
```

Now only search vectors inside cluster B.

Instead of scanning all rows.

---

# 13. Creating an IVFFlat Index

Example:

```sql
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

Explanation:

| Part              | Meaning            |
| ----------------- | ------------------ |
| ivfflat           | index type         |
| vector_cosine_ops | cosine similarity  |
| lists=100         | number of clusters |

---

# 14. How lists Work

`lists` = number of clusters.

Example:

```
1 million vectors
lists = 100
```

Each cluster contains:

```
~10,000 vectors
```

Search becomes much faster.

---

# 15. Query with IVFFlat

Example search:

```sql
SELECT text
FROM documents
ORDER BY embedding <=> '[0.9,0.1,0.3]'
LIMIT 5;
```

Database will:

```
1. find closest clusters
2. search vectors inside cluster
3. return nearest results
```

---

# 16. Speed Comparison

Without index:

```
scan all rows
O(N)
```

With IVFFlat:

```
scan few clusters
O(log N)
```

Massive speed improvement.

---

# 17. Important IVFFlat Parameter

Another parameter:

```
probes
```

Example:

```sql
SET ivfflat.probes = 10;
```

Meaning:

```
search 10 clusters
```

Tradeoff:

| probes | effect        |
| ------ | ------------- |
| small  | faster        |
| large  | more accurate |

---

# 18. Real AI Application Example

Imagine a **YouTube semantic search system**.

Pipeline:

```
YouTube video
↓
extract transcript
↓
split transcript
↓
generate embeddings
↓
store vectors in pgvector
```

Example table:

```
video_chunks
-------------------------
id
transcript
embedding
```

Search query:

```
"how do python lists work?"
```

System:

```
query → embedding
```

Database search:

```
ORDER BY embedding <=> query_vector
```

Returns most relevant transcript chunk.

---

# 19. Why pgvector Became Popular

Because it allows **AI search inside PostgreSQL**.

Before pgvector:

```
database + external vector database
```

Example:

```
PostgreSQL + Pinecone
```

Now:

```
PostgreSQL alone
```

Simpler architecture.

---

# 20. Complete System Architecture

Typical AI search system:

```
User question
↓
embedding model
↓
vector
↓
pgvector similarity search
↓
retrieve documents
↓
LLM generates answer
```

This is the core of **RAG systems**.

---

# 21. Summary

pgvector is a PostgreSQL extension that enables:

### Vector storage

```
VECTOR(1536)
```

### Similarity search

```
<-> Euclidean
<=> Cosine
<#> Inner product
```

### Vector indexing

```
IVFFlat
HNSW
```

### Fast AI search

```
semantic search
recommendation systems
RAG pipelines
```

---

✅ Simple mental model:

```
Text
↓
Embedding model
↓
Vector (numbers)
↓
Stored in pgvector
↓
Similarity search finds closest meaning
```

---

# 1. Does the Database Compute Euclidean Distance?

Yes. When using **pgvector** inside **PostgreSQL**, the database itself computes vector distances.

Example query:

```sql
SELECT *
FROM video_chunks
ORDER BY embedding <-> '[0.12,0.3,0.7]'
LIMIT 5;
```

The operator:

```text
<->
```

means **Euclidean distance**.

So PostgreSQL calculates the distance between the **query vector** and every **stored vector**.

---

## What Euclidean Distance Means

Euclidean distance measures **how far two vectors are in space**.

Formula:

```
distance = √((a1-b1)² + (a2-b2)² + ... + (an-bn)²)
```

Where:

```
A = stored vector
B = query vector
```

---

## Example

Suppose we store embeddings:

| id | embedding |
| -- | --------- |
| 1  | [1,2]     |
| 2  | [4,6]     |
| 3  | [1.1,2.1] |

User query vector:

```
[1,2]
```

Distance calculations:

### Row 1

```
√((1-1)² + (2-2)²)
= √(0+0)
= 0
```

Perfect match.

---

### Row 2

```
√((4-1)² + (6-2)²)
= √(9 + 16)
= √25
= 5
```

Far away.

---

### Row 3

```
√((1.1-1)² + (2.1-2)²)
= √(0.01 + 0.01)
= √0.02
= 0.14
```

Very similar.

---

## Query Result

```
ORDER BY distance
```

Sorted results:

| id | distance |
| -- | -------- |
| 1  | 0        |
| 3  | 0.14     |
| 2  | 5        |

So the database returns **most similar vectors first**.

---

# 2. What Happens Internally in PostgreSQL

When executing:

```sql
ORDER BY embedding <-> query_vector
```

PostgreSQL:

1️⃣ reads vector from row
2️⃣ reads query vector
3️⃣ subtracts each dimension
4️⃣ squares the difference
5️⃣ sums them
6️⃣ computes square root

Example with 1536 dimensions:

```
1536 subtraction operations
1536 squares
1536 additions
1 square root
```

This happens **for every row** unless an index is used.

---

# 3. When Index Exists (IVFFlat)

If an **IVFFlat index** exists:

```sql
CREATE INDEX ON video_chunks
USING ivfflat (embedding vector_cosine_ops);
```

Then the process changes.

Instead of checking every row:

```
1. find closest clusters
2. search inside cluster
3. compute distances
```

So Euclidean distance still happens — but **only for fewer vectors**.

---
To find the "closest" items in a vector space, we need a way to quantify distance. While simple in theory, the choice of metric and the algorithm used to calculate it change based on the size and type of your data.

---

## 1. Most Common Distance Metrics

The "closeness" between two vectors ($A$ and $B$) is generally measured using one of these three metrics. The best one depends entirely on how your machine learning model was trained.

| Metric | Formula | When to Use It |
| --- | --- | --- |
| **Euclidean (L2)** | $\sqrt{\sum (A_i - B_i)^2}$ | When **absolute magnitude** and scale matter (e.g., image recognition, sensor data). It measures the straight-line distance. |
| **Cosine Similarity** | $\frac{A \cdot B}{\|A\| \|$ | When only **orientation** matters (e.g., NLP, text search). It ignores how long a document is and focuses on the "direction" of the topics. |
| **Dot Product** | $\sum (A_i \times B_i)$ | When both **direction and magnitude** matter. Common in recommendation systems where a "longer" vector might represent a more active user. |

> **Pro Tip:** If your vectors are **normalized** (all have a length of 1), Cosine Similarity and Dot Product become mathematically identical.

---

## 2. How ANN Algorithms Solve the "Speed Problem"

In a standard **k-Nearest Neighbor (kNN)** search, the computer compares your query to every single item in the database. If you have 100 million vectors, this is impossibly slow.

**Approximate Nearest Neighbor (ANN)** algorithms solve this by using the distance metrics above to build "shortcuts." They don't look at everything; they look only at the most promising "neighborhoods."

### The Two Most Common Strategies:

### **A. HNSW (Graph-Based)**

Imagine a map where some roads are highways (long jumps) and others are city streets (short jumps).

* **The Solve:** HNSW creates a multi-layered graph. The top layers have few points and long connections. The search starts there to find the general "area" and then zooms in to lower, denser layers to find the specific neighbors.
* **Relation to Metrics:** In every "hop" from node to node, the algorithm uses a distance metric (like Cosine or L2) to decide which neighbor is closer to the query.

### **B. IVF (Cluster-Based)**

Think of this like a library where books are grouped by genre (clusters).

* **The Solve:** The algorithm divides the vector space into "cells" (Voronoi cells) around central points called centroids.
* **The Process:** 1. The query is compared to the **centroids** first.
2. The search is narrowed down to only the 1 or 2 closest clusters.
3. The algorithm then does a precise distance calculation within those clusters only.
* **Relation to Metrics:** Distance metrics are used twice: first to find the closest cluster, then to rank the items inside it.

---

## Summary: How They Work Together

1. **The Metric** defines what "near" means (is it the angle or the distance?).
2. **The ANN Algorithm** organizes the data so that the computer only has to run that metric calculation a few hundred times instead of a few million times.

I’ll explain **vector indexing from the ground up** so a beginner can understand:

1️⃣ What vector indexing is
2️⃣ Why it is needed
3️⃣ How similarity search works without an index
4️⃣ How vector indexes work
5️⃣ **IVFFlat indexing (deep internal mechanics)**
6️⃣ **HNSW indexing (why it’s faster)**
7️⃣ Practical examples in **pgvector** with **PostgreSQL**.

---

# 1. The Problem Vector Indexing Solves

Imagine a table:

| id | text              | embedding        |
| -- | ----------------- | ---------------- |
| 1  | Dogs are friendly | [0.9,0.1,0.3]    |
| 2  | Cats are cute     | [0.85,0.12,0.28] |
| 3  | Cars are fast     | [-0.3,0.8,0.2]   |

Now a user asks:

```
"animals"
```

Your AI model converts the query into a vector:

```
[0.88,0.11,0.29]
```

You run:

```sql
SELECT *
FROM documents
ORDER BY embedding <=> '[0.88,0.11,0.29]'
LIMIT 5;
```

The database must:

```
compare query vector with EVERY vector in table
```

---

## Example with 1M vectors

```
1,000,000 distance calculations
```

Distance calculation requires:

```
1536 subtractions
1536 squares
1536 additions
1 square root
```

Total operations:

```
~3000 operations × 1M rows
```

Very slow.

---

# 2. What Vector Indexing Does

Vector indexing **reduces the number of vectors you compare**.

Instead of:

```
compare query with ALL vectors
```

You do:

```
compare query with small subset
```

Example:

```
1,000,000 vectors
→ search only 2,000 vectors
```

Huge speed improvement.

---

# 3. Types of Vector Indexes

Common algorithms:

| Method  | Idea               |
| ------- | ------------------ |
| IVFFlat | cluster vectors    |
| HNSW    | graph navigation   |
| LSH     | hashing            |
| PQ      | compressed vectors |

In **pgvector**, main ones are:

```
IVFFlat
HNSW
```

---

# 4. Understanding Vector Space

Vectors exist in **high dimensional space**.

Example:

2-D vectors:

```
(1,2)
(4,6)
```

Visual:

```
Y
|
|        B
|
|   A
|
+-------------- X
```

Distance:

```
A → B
```

In embeddings:

```
1536 dimensions
```

Impossible to visualize.

---

# 5. Brute Force Search

Without index:

```
for each vector in database:
    compute distance
sort results
return top k
```

Complexity:

```
O(N)
```

For large datasets this is slow.

---

# 6. IVFFlat Index (Concept)

IVFFlat stands for:

```
Inverted File with Flat vectors
```

Idea:

```
cluster vectors into groups
```

Instead of scanning whole dataset.

---

# 7. Step 1 — Training Phase

Before creating index, pgvector performs **clustering**.

Algorithm used:

```
k-means clustering
```

Goal:

```
divide vectors into groups
```

Example dataset:

```
10 vectors
```

We choose:

```
lists = 3
```

Clusters formed:

```
Cluster A
Cluster B
Cluster C
```

---

# 8. Example Clustering

Vectors:

```
[0.9,0.1]
[0.85,0.12]
[0.87,0.15]

[-0.3,0.8]
[-0.35,0.75]

[0.2,-0.8]
[0.25,-0.75]
```

Clusters:

```
Cluster 1 → animal vectors
Cluster 2 → vehicle vectors
Cluster 3 → other vectors
```

Each cluster has a **centroid**.

Centroid example:

```
Cluster 1 center:
[0.87,0.12]
```

---

# 9. Step 2 — Assign Vectors

After clustering:

Each vector is assigned to its nearest centroid.

Example:

```
Cluster 1
  v1
  v2
  v3

Cluster 2
  v4
  v5

Cluster 3
  v6
  v7
```

Database stores:

```
cluster id → vectors
```

---

# 10. IVFFlat Search Process

When query arrives:

```
query vector
```

Step 1:

```
compare query with centroids
```

Example:

```
distance(query, centroid1)
distance(query, centroid2)
distance(query, centroid3)
```

Find nearest cluster.

---

Step 2:

Search **only vectors inside that cluster**.

Instead of whole dataset.

Example:

```
dataset size = 1M
cluster size = 10k
```

Search cost:

```
10k comparisons instead of 1M
```

---

# 11. IVFFlat in SQL

Create index:

```sql
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

Meaning:

```
100 clusters
```

---

# 12. Parameter: Lists

`lists` controls cluster count.

Example:

```
1M vectors
lists = 100
```

Each cluster:

```
~10k vectors
```

Tradeoff:

| lists | effect                 |
| ----- | ---------------------- |
| small | faster index build     |
| large | better search accuracy |

---

# 13. Parameter: Probes

During search:

```
database searches N clusters
```

Example:

```sql
SET ivfflat.probes = 10;
```

Meaning:

```
search 10 clusters
```

Tradeoff:

| probes | effect        |
| ------ | ------------- |
| low    | faster        |
| high   | more accurate |

---

# 14. IVFFlat Limitations

IVFFlat is **approximate search**.

Meaning:

```
may miss exact nearest neighbor
```

But usually accuracy:

```
95–99%
```

Much faster.

---

# 15. HNSW Index (Modern Method)

HNSW stands for:

```
Hierarchical Navigable Small World
```

Used by many AI systems.

Idea:

```
build a graph of vectors
```

Where nodes represent vectors.

---

# 16. Graph Example

Vectors become nodes:

```
A --- B --- C
|     |
D --- E
```

Edges connect **similar vectors**.

Meaning:

```
neighbors in embedding space
```

---

# 17. Search in HNSW

Query process:

Start from entry point.

Then navigate graph:

```
jump to closer neighbors
```

Like greedy search.

Example:

```
start node → find closer neighbor → repeat
```

Until best match found.

---

# 18. Hierarchical Layers

HNSW uses multiple layers.

Top layer:

```
few nodes
long connections
```

Bottom layer:

```
many nodes
short connections
```

Structure:

```
Layer 3 (few nodes)
   ↓
Layer 2
   ↓
Layer 1
   ↓
Layer 0 (all nodes)
```

Search:

```
start at top
navigate downward
```

This reduces search cost dramatically.

---

# 19. Why HNSW Is Faster

IVFFlat:

```
search clusters
```

HNSW:

```
navigate graph
```

Graph traversal is extremely efficient.

Typical complexity:

```
O(log N)
```

While brute force:

```
O(N)
```

---

# 20. Example Search Path

Imagine graph:

```
A --- B --- C
      |
      D --- E
```

Query vector close to E.

Search:

```
start at A
A → B
B → D
D → E
```

Stop when no better neighbor exists.

---

# 21. HNSW Advantages

| Feature          | Benefit                   |
| ---------------- | ------------------------- |
| very fast search | milliseconds              |
| high recall      | ~99% accuracy             |
| dynamic insert   | works with streaming data |

---

# 22. HNSW Disadvantages

| Problem          | reason            |
| ---------------- | ----------------- |
| large memory     | graph structure   |
| slow index build | complex structure |

---

# 23. IVFFlat vs HNSW

| Feature      | IVFFlat | HNSW      |
| ------------ | ------- | --------- |
| Speed        | fast    | faster    |
| Accuracy     | good    | excellent |
| Memory       | small   | large     |
| Index build  | fast    | slow      |
| Dataset size | medium  | huge      |

---

# 24. Example Use Cases

IVFFlat used for:

```
medium datasets
millions of vectors
```

HNSW used for:

```
large AI systems
tens of millions vectors
```

Examples:

* vector search engines
* recommendation systems
* AI chat retrieval

---

# 25. Example AI Pipeline

Typical system:

```
documents
↓
embedding model
↓
vector database
↓
vector index
↓
similarity search
↓
LLM answer
```

Index enables **real-time search**.

---

# 26. Example with pgvector

Create table:

```sql
CREATE TABLE documents (
 id SERIAL PRIMARY KEY,
 text TEXT,
 embedding VECTOR(1536)
);
```

Create HNSW index:

```sql
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops);
```

Now search:

```sql
SELECT text
FROM documents
ORDER BY embedding <=> query_vector
LIMIT 5;
```

Search becomes extremely fast.

---

# 27. Beginner Mental Model

Think of vectors like **cities on a map**.

Without index:

```
check distance to every city
```

IVFFlat:

```
first find nearest country
then search cities inside country
```

HNSW:

```
use highways between cities
navigate quickly to destination
```

---

# 28. Summary

Vector indexing speeds up similarity search.

Main methods in **pgvector**:

### IVFFlat

```
clusters vectors
search within clusters
```

### HNSW

```
build graph of vectors
navigate graph to nearest neighbor
```

Both allow efficient vector search in **PostgreSQL**.

---

✅ If you'd like, I can also explain **how FAISS (used by Meta AI) implements vector search internally and why it inspired pgvector**, which reveals the deeper math behind modern AI retrieval systems.
