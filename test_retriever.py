from rag.document_processor import create_documents, split_documents
from rag.vector_store import create_vector_store
from rag.retriever import retrieve_relevant_chunks


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
print("RAG RETRIEVER TEST")
print("==============================")


documents = create_documents(sources)

chunks = split_documents(
    documents,
    chunk_size=300,
    chunk_overlap=50,
)

vector_store = create_vector_store(chunks)


query = "How can AI help doctors?"

print("\nUser Query:")
print(query)

results = retrieve_relevant_chunks(
    vector_store,
    query,
    k=2,
)


print("\nRetrieved Relevant Chunks:")

for i, result in enumerate(results, 1):

    print(f"\n--- Result {i} ---")

    print("Content:")
    print(result.page_content)

    print("\nSource:")
    print(result.metadata.get("title"))

    print("URL:")
    print(result.metadata.get("url"))