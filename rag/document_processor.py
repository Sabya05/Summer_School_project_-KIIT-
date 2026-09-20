"""Convert Tavily web results into chunks for RAG."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_documents(sources: list[dict]) -> list[Document]:
    """Convert Tavily sources into LangChain Documents."""

    documents = []

    for source in sources:
        content = source.get("content", "").strip()

        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "title": source.get("title", "Untitled source"),
                    "url": source.get("url", ""),
                },
            )
        )

    return documents


def split_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Split documents into smaller overlapping chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_documents(documents)