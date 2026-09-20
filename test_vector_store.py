from rag.document_processor import create_documents, split_documents
from rag.vector_store import create_vector_store


sources = [
    {
        "title": "AI Healthcare",
        "url": "https://example.com/ai-healthcare",
        "content": (
            "Artificial intelligence is increasingly being used in healthcare. "
            "AI systems can help doctors analyze medical images and identify "
            "patterns in patient data."
        ),
    },
    {
        "title": "AI Education",
        "url": "https://example.com/ai-education",
        "content": (
            "Artificial intelligence is changing education through personalized "
            "learning systems, automated feedback, and intelligent tutoring tools."
        ),
    },
]


print("\n==============================")
print("VECTOR STORE TEST")
print("==============================")

documents = create_documents(sources)
chunks = split_documents(
    documents,
    chunk_size=300,
    chunk_overlap=50,
)

print("Documents:", len(documents))
print("Chunks:", len(chunks))

print("\nCreating Chroma vector store...")

vector_store = create_vector_store(chunks)

print("Vector store created successfully!")

print("\nTesting semantic search...")

results = vector_store.similarity_search(
    "How is AI being used in healthcare?",
    k=2,
)

print("\nRetrieved results:")

for i, result in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print("Content:", result.page_content)
    print("Title:", result.metadata.get("title"))
    print("URL:", result.metadata.get("url"))