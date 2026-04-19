"""Extract plain text from uploaded bytes (txt / pdf)."""

from __future__ import annotations

import io
from typing import Literal

from pypdf import PdfReader

SourceType = Literal["text", "pdf"]


def detect_source_type(filename: str) -> SourceType | None:
    lower = filename.lower()
    if lower.endswith(".txt"):
        return "text"
    if lower.endswith(".pdf"):
        return "pdf"
    return None


def extract_text(filename: str, data: bytes) -> tuple[str, SourceType]:
    """Return (plain_text, source_type). Raises ValueError if unsupported or empty."""
    kind = detect_source_type(filename)
    if kind is None:
        raise ValueError("Only .txt and .pdf uploads are supported")

    if kind == "text":
        text = data.decode("utf-8", errors="replace")
    else:
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts)

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("No extractable text in file")
    return cleaned, kind
