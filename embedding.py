"""Local sentence-transformers embeddings; no provider tokens are consumed."""

from __future__ import annotations

import os
import threading
from functools import lru_cache

MODEL_NAME = os.getenv(
    "LOCAL_EMBED_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
_MODEL_LOCK = threading.Lock()


@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is not installed; run: pip install -r requirements.txt"
        ) from exc
    with _MODEL_LOCK:
        return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = _model().encode(
        texts,
        batch_size=min(32, len(texts)),
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return [vector.tolist() for vector in vectors]


def embedding_model_name() -> str:
    return MODEL_NAME
