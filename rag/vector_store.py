"""Vector store for NewsLens AI RAG."""

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import GEMINI_API_KEY


def create_embeddings():
    """Create the Google Gemini embedding model."""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GEMINI_API_KEY,
    )


def create_vector_store(documents):
    """Create an in-memory Chroma vector store from documents."""

    embeddings = create_embeddings()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
    )

    return vector_store