from rag.rag_pipeline import run_rag


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


query = "How can AI help doctors?"


print("\n==============================")
print("COMPLETE RAG PIPELINE TEST")
print("==============================")


results = run_rag(
    query=query,
    sources=sources,
    k=2,
)


print("\nQuery:")
print(query)

print("\nRelevant Sources:")

for i, source in enumerate(results, 1):

    print(f"\n--- Source {i} ---")

    print("Title:", source["title"])
    print("URL:", source["url"])

    print("Content:")
    print(source["content"])