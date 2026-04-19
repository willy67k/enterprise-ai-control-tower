"""Split long text into overlapping chunks for embedding."""


def chunk_text(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    """Character-based windows with overlap; skips empty segments."""
    text = text.strip()
    if not text:
        return []
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    overlap = max(0, min(overlap, chunk_size - 1))
    step = max(chunk_size - overlap, 1)

    chunks: list[str] = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start += step
    return chunks
