"""Split long text into overlapping chunks for embedding."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    """Prefer splits at ``\\n\\n``, then ``\\n``, then spaces (LangChain recursive splitter)."""
    text = text.strip()
    if not text:
        return []
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    overlap = max(0, min(overlap, chunk_size - 1))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    return [c for c in chunks if c.strip()]
