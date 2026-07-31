"""Rubric-driven retrieval over precomputed local CV embeddings."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from embedding import embed_texts


@dataclass(frozen=True)
class StoredChunk:
    id: str
    section: str
    text: str
    embedding: list[float]


@dataclass(frozen=True)
class RetrievedMatch:
    criterion_id: str
    chunk_id: str
    similarity: float


@dataclass(frozen=True)
class RetrievalResult:
    chunks: list[StoredChunk]
    matches: list[RetrievedMatch]


def _query_text(criterion: object) -> str:
    return " ".join(
        value
        for value in (
            str(getattr(criterion, "name", "")),
            str(getattr(criterion, "description", "")),
        )
        if value
    )


def retrieve_for_rubric(
    chunks: list[StoredChunk],
    rubric: list[object],
    top_k: int,
) -> RetrievalResult:
    if not chunks or not rubric:
        return RetrievalResult(chunks=[], matches=[])
    chunk_matrix = np.asarray([chunk.embedding for chunk in chunks], dtype=np.float32)
    query_matrix = np.asarray(embed_texts([_query_text(item) for item in rubric]), dtype=np.float32)
    if chunk_matrix.ndim != 2 or query_matrix.ndim != 2 or chunk_matrix.shape[1] != query_matrix.shape[1]:
        raise ValueError("Stored and query embedding dimensions do not match")

    scores = query_matrix @ chunk_matrix.T
    matches: list[RetrievedMatch] = []
    selected_ids: set[str] = set()
    for criterion_index, criterion in enumerate(rubric):
        count = min(top_k, len(chunks))
        ranked = np.argsort(scores[criterion_index])[::-1][:count]
        for chunk_index in ranked:
            chunk = chunks[int(chunk_index)]
            selected_ids.add(chunk.id)
            matches.append(
                RetrievedMatch(
                    criterion_id=str(getattr(criterion, "id")),
                    chunk_id=chunk.id,
                    similarity=round(float(scores[criterion_index, chunk_index]), 4),
                )
            )
    return RetrievalResult(
        chunks=[chunk for chunk in chunks if chunk.id in selected_ids],
        matches=matches,
    )
