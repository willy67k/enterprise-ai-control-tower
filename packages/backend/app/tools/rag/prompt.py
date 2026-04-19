"""RAG prompt construction."""


def build_rag_prompt(question: str, contexts: list[str]) -> str:
    if not contexts:
        return (
            "There is no retrieved document context. Answer that you have no "
            f"supporting snippets, then respond briefly to: {question}"
        )
    joined = "\n\n---\n\n".join(contexts)
    return (
        "You are a helpful assistant. Use only the following context snippets to "
        "answer the question. If the answer is not contained in the context, say you "
        "do not know based on the provided documents.\n\n"
        f"Context:\n{joined}\n\nQuestion:\n{question}"
    )
