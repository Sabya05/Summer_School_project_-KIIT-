"""Retrieve relevant chunks from the Chroma vector store."""


def retrieve_relevant_chunks(vector_store, query: str, k: int = 5):
    """
    Retrieve the most relevant document chunks for a user query.
    """

    results = vector_store.similarity_search(
        query,
        k=k,
    )

    return results