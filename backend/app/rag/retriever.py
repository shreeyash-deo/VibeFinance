"""
backend/app/rag/retriever.py - Semantic Vector Retrieval Engine
"""

import os
from pathlib import Path
from typing import Any
from backend.app.config import settings
from backend.app.rag.chunker import parse_markdown_with_frontmatter, chunk_document
from backend.app.rag.embeddings import get_text_embedding, cosine_similarity

class FilingsRetriever:
    def __init__(self, filings_dir: Path | None = None):
        self.filings_dir = Path(filings_dir) if filings_dir else settings.FILINGS_DIR
        self._chunks: list[dict[str, Any]] = []
        self._by_id: dict[str, dict[str, Any]] = {}
        self._indexed = False

    def load_and_index(self):
        """Loads and chunks all markdown files from the filings directory."""
        if self._indexed and self._chunks:
            return

        self._chunks.clear()
        self._by_id.clear()

        if not self.filings_dir.exists():
            return

        for filepath in self.filings_dir.glob("*.md"):
            try:
                content = filepath.read_text(encoding="utf-8")
                doc_id = filepath.stem
                meta, body = parse_markdown_with_frontmatter(content)
                ticker = meta.get("ticker", doc_id.split("_")[0]).upper()

                chunks = chunk_document(doc_id=doc_id, ticker=ticker, meta=meta, body=body)
                for ch in chunks:
                    self._chunks.append(ch)
                    self._by_id[ch["id"]] = ch
            except Exception as e:
                print(f"Error indexing {filepath}: {e}")

        self._indexed = True

    def get_chunk_by_id(self, chunk_id: str) -> dict[str, Any] | None:
        self.load_and_index()
        return self._by_id.get(chunk_id)

    def retrieve(self, ticker: str, query: str, top_k: int = 8) -> list[dict[str, Any]]:
        self.load_and_index()
        ticker = ticker.upper()

        # Hard-filter on ticker
        candidates = [c for c in self._chunks if c["ticker"] == ticker]
        if not candidates:
            return []

        query_emb = get_text_embedding(query)

        scored = []
        for ch in candidates:
            score = cosine_similarity(query_emb, ch["embedding"])
            # Slight recency boost if dated recently
            doc_date = ch.get("doc_date", "2026-01-01")
            if "2026" in doc_date:
                score += 0.05
            scored.append((score, ch))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, ch in scored[:top_k]:
            item = dict(ch)
            item["score"] = round(float(s), 4)
            results.append(item)
        return results

retriever = FilingsRetriever()

