"""
GovAgent — FAISS Vector Store for Regulation Clauses
======================================================
Builds a FAISS index from the regulation corpus using sentence-transformers
for local embeddings (no API key needed).

Provides:
- ``build_index()`` — create and persist the FAISS index
- ``query_regulations(query, top_k)`` — semantic search over regulation clauses
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.mcp.regulations import REGULATION_CLAUSES

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_INDEX_DIR = _PROJECT_ROOT / "data" / "faiss_index"
_INDEX_FILE = _INDEX_DIR / "regulations.index"
_METADATA_FILE = _INDEX_DIR / "metadata.json"

# ---------------------------------------------------------------------------
# Embedding model (lazy-loaded)
# ---------------------------------------------------------------------------

_model = None


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of text strings into vectors."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    # Normalise for cosine similarity via inner product
    faiss.normalize_L2(embeddings)
    return embeddings


# ---------------------------------------------------------------------------
# Build index
# ---------------------------------------------------------------------------

def build_index() -> None:
    """Build and persist the FAISS index from the regulation corpus.

    Creates ``data/faiss_index/regulations.index`` and
    ``data/faiss_index/metadata.json``.
    """
    print(f"  Building FAISS index from {len(REGULATION_CLAUSES)} clauses ...")

    # Prepare texts for embedding: combine title + article + text for richer matching
    texts = []
    metadata = []
    for clause in REGULATION_CLAUSES:
        combined = (
            f"{clause['regulation']} {clause['article']}: {clause['title']}. "
            f"{clause['text']}"
        )
        texts.append(combined)
        metadata.append(clause)

    # Embed
    embeddings = _embed_texts(texts)
    dim = embeddings.shape[1]

    # Build FAISS index (inner product since vectors are normalised)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Persist
    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(_INDEX_FILE))
    with open(_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"  Index saved: {_INDEX_FILE} ({index.ntotal} vectors, dim={dim})")


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

_index_cache: faiss.Index | None = None
_metadata_cache: list[dict] | None = None


def _load_index() -> tuple[faiss.Index, list[dict]]:
    """Load the persisted FAISS index and metadata (with caching)."""
    global _index_cache, _metadata_cache
    if _index_cache is not None and _metadata_cache is not None:
        return _index_cache, _metadata_cache

    if not _INDEX_FILE.exists():
        # Auto-build if not present
        build_index()

    _index_cache = faiss.read_index(str(_INDEX_FILE))
    with open(_METADATA_FILE, "r", encoding="utf-8") as f:
        _metadata_cache = json.load(f)

    return _index_cache, _metadata_cache


def query_regulations(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Semantic search over the regulation corpus.

    Parameters
    ----------
    query : str
        Natural language query (e.g. "automated decision making rights").
    top_k : int
        Number of results to return.

    Returns
    -------
    list[dict]
        Top-K matching regulation clauses, each augmented with a
        ``similarity_score`` field (0-1, higher = more relevant).
    """
    index, metadata = _load_index()

    # Embed the query
    query_vec = _embed_texts([query])

    # Search
    scores, indices = index.search(query_vec, min(top_k, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        clause = dict(metadata[idx])
        clause["similarity_score"] = round(float(score), 4)
        results.append(clause)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build_index()
    print("\n  Test query: 'automated decision making'")
    results = query_regulations("automated decision making", top_k=3)
    for r in results:
        print(f"    [{r['similarity_score']:.3f}] {r['regulation']} {r['article']}: {r['title']}")
