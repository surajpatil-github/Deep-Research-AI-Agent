# tools/vectorstore.py
from __future__ import annotations

import os
from typing import Iterable, List, Tuple

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


class VectorStore:
    """
    Tiny in-memory vector store using OpenAI embeddings.
    """

    def __init__(self) -> None:
        self.client = OpenAI()
        self.texts: List[str] = []
        self.metas: List[dict] = []
        self.vectors: np.ndarray = np.empty((0, 1536), dtype=np.float32)

    def _embed(self, texts: Iterable[str]) -> np.ndarray:
        texts = list(texts)
        resp = self.client.embeddings.create(model=_EMBED_MODEL, input=texts)
        return np.array([d.embedding for d in resp.data], dtype=np.float32)

    def add(self, texts: List[str], metadatas: List[dict] | None = None) -> None:
        if not texts:
            return
        vecs = self._embed(texts)
        self.vectors = vecs if self.vectors.size == 0 else np.vstack([self.vectors, vecs])
        self.texts.extend(texts)
        self.metas.extend(metadatas or [{} for _ in texts])

    def _cosine_topk(self, q: np.ndarray, k: int) -> List[Tuple[int, float]]:
        if self.vectors.size == 0:
            return []
        A = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-8)
        qn = q / (np.linalg.norm(q) + 1e-8)
        sims = A @ qn
        idx = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i])) for i in idx]

    def similarity_search(self, query: str, k: int = 5) -> List[dict]:
        qv = self._embed([query])[0]
        hits = self._cosine_topk(qv, k)
        return [{"text": self.texts[i], "metadata": self.metas[i], "score": s} for i, s in hits]
