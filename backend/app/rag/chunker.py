"""
backend/app/rag/chunker.py - Document Parsing & Chunking with Frontmatter Extraction
"""

import os
import re
from typing import Any
from backend.app.rag.embeddings import get_text_embedding

def parse_markdown_with_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parses YAML-style frontmatter from markdown content.
    """
    meta = {}
    body = content
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        front_text = match.group(1)
        body = content[match.end():]
        for line in front_text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body.strip()

def chunk_document(doc_id: str, ticker: str, meta: dict[str, Any], body: str, chunk_size: int = 500, overlap: int = 80) -> list[dict[str, Any]]:
    """
    Splits document body into chunks, preserving section titles and frontmatter metadata.
    """
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_words = 0
    chunk_index = 0

    for p in paragraphs:
        words = p.split()
        if current_words + len(words) > chunk_size and current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunk_embedding = get_text_embedding(chunk_text)
            chunks.append({
                "id": f"{doc_id}_c{chunk_index}",
                "document_id": doc_id,
                "ticker": ticker.upper(),
                "chunk_index": chunk_index,
                "page": int(meta.get("page", 1)),
                "title": meta.get("title", f"{ticker} Corporate Document"),
                "doc_type": meta.get("doc_type", "FILING"),
                "doc_date": meta.get("date", "2026-10-01"),
                "source_label": meta.get("source_label", "SYNTHETIC"),
                "text": chunk_text,
                "embedding": chunk_embedding,
                "meta_info": meta
            })
            chunk_index += 1
            # Retain overlap from last paragraph
            current_chunk = [p]
            current_words = len(words)
        else:
            current_chunk.append(p)
            current_words += len(words)

    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunk_embedding = get_text_embedding(chunk_text)
        chunks.append({
            "id": f"{doc_id}_c{chunk_index}",
            "document_id": doc_id,
            "ticker": ticker.upper(),
            "chunk_index": chunk_index,
            "page": int(meta.get("page", 1)),
            "title": meta.get("title", f"{ticker} Corporate Document"),
            "doc_type": meta.get("doc_type", "FILING"),
            "doc_date": meta.get("date", "2026-10-01"),
            "source_label": meta.get("source_label", "SYNTHETIC"),
            "text": chunk_text,
            "embedding": chunk_embedding,
            "meta_info": meta
        })

    return chunks

