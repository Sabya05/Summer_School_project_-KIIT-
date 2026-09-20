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


queries = [
    "How can AI help doctors?",
    "How is AI changing education?",
]


print("\n==============================")
print("RAG RELEVANCE TEST")
print("==============================")


for query in queries:

    print("\n================================")
    print("QUERY:", query)
    print("================================")

    results = run_rag(
        query=query,
        sources=sources,
        k=1,
    )

    for i, source in enumerate(results, 1):

        print(f"\nResult {i}")
        print("Title:", source["title"])
        print("Content:", source["content"])