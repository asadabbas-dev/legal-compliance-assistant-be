"""Semantic/token-aware chunking helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

CHARS_PER_TOKEN_EST = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN_EST)


def detect_section(text: str) -> str | None:
    line = text.strip().splitlines()[0] if text.strip() else ""
    if not line:
        return None
    if len(line) < 120 and line.endswith(":"):
        return line
    if len(line) < 120 and line.isupper():
        return line
    if re.match(r"^(section|article|\d+\.)\s+", line, flags=re.I):
        return line
    return None


@dataclass
class ChunkPayload:
    page_number: int
    section: str | None
    chunk_text: str
    token_count: int


def semantic_chunk_pages(
    pages: list[tuple[str, int]],
    chunk_size_tokens: int,
    overlap_tokens: int,
) -> list[ChunkPayload]:
    chunk_size_chars = max(200, chunk_size_tokens * CHARS_PER_TOKEN_EST)
    overlap_chars = max(0, overlap_tokens * CHARS_PER_TOKEN_EST)
    out: list[ChunkPayload] = []

    for page_text, page_number in pages:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page_text) if p.strip()]
        if not paragraphs:
            continue
        buf = ""
        section: str | None = None

        for para in paragraphs:
            para_section = detect_section(para)
            if para_section:
                section = para_section
            candidate = para if not buf else f"{buf}\n\n{para}"
            if len(candidate) <= chunk_size_chars:
                buf = candidate
                continue

            if buf.strip():
                out.append(
                    ChunkPayload(
                        page_number=page_number,
                        section=section,
                        chunk_text=buf.strip(),
                        token_count=estimate_tokens(buf),
                    )
                )
                if overlap_chars > 0:
                    tail = buf[-overlap_chars:]
                    buf = f"{tail}\n\n{para}".strip()
                else:
                    buf = para
            else:
                # Single huge paragraph fallback
                start = 0
                while start < len(para):
                    end = start + chunk_size_chars
                    part = para[start:end].strip()
                    if part:
                        out.append(
                            ChunkPayload(
                                page_number=page_number,
                                section=section,
                                chunk_text=part,
                                token_count=estimate_tokens(part),
                            )
                        )
                    start = max(end - overlap_chars, end)
                buf = ""

        if buf.strip():
            out.append(
                ChunkPayload(
                    page_number=page_number,
                    section=section,
                    chunk_text=buf.strip(),
                    token_count=estimate_tokens(buf),
                )
            )

    return out
