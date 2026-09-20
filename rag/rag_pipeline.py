"""Complete RAG pipeline for NewsLens AI."""

from rag.document_processor import create_documents, split_documents
from rag.vector_store import create_vector_store
from rag.retriever import retrieve_relevant_chunks


def run_rag(query: str, sources: list[dict], k: int = 5) -> list[dict]:
    """
    Run the complete RAG pipeline.

    Flow:
        Sources
        → Documents
        → Chunks
        → Embeddings
        → Chroma
        → Relevant chunks
    """

    # 1. Convert Tavily sources into LangChain documents
    documents = create_documents(sources)

    if not documents:
        return []

    # 2. Split documents into smaller chunks
    chunks = split_documents(documents)

    if not chunks:
        return []

    # 3. Create vector store
    vector_store = create_vector_store(chunks)

    # 4. Retrieve chunks relevant to the user's question
    relevant_chunks = retrieve_relevant_chunks(
        vector_store,
        query,
        k=k,
    )

    # 5. Convert LangChain Documents back to our source format
    results = []

    for chunk in relevant_chunks:
        results.append(
            {
                "title": chunk.metadata.get("title", "Untitled source"),
                "url": chunk.metadata.get("url", ""),
                "content": chunk.page_content,
            }
        )

    return results