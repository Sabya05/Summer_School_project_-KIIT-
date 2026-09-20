from rag.document_processor import create_documents, split_documents

sources = [
    {
        "title": "Test Article",
        "url": "https://example.com",
        "content": (
            "Artificial intelligence is changing many industries. "
            "Healthcare, finance, education, and software development "
            "are increasingly using AI technologies."
        ),
    }
]

documents = create_documents(sources)

chunks = split_documents(documents, chunk_size=100, chunk_overlap=20)

print("\n==============================")
print("RAG DOCUMENT TEST")
print("==============================")

print("Documents:", len(documents))
print("Chunks:", len(chunks))

for i, chunk in enumerate(chunks, 1):
    print(f"\n--- Chunk {i} ---")
    print(chunk.page_content)
    print("Metadata:", chunk.metadata)