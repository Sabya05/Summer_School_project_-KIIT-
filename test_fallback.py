from services.ai_orchestrator import run_ai_research


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
print("GEMINI → GROQ FALLBACK TEST")
print("==============================")


result = run_ai_research(
    query="How is artificial intelligence being used in healthcare?",
    mode="simple",
    sources=sources,
)


print("\n==============================")
print("FINAL RESULT")
print("==============================")

print("Provider:", result.get("provider"))
print("RAG used:", result.get("rag_used"))

print("\nAnswer:")
print(result.get("answer"))

print("\nFollow-ups:")

for question in result.get("followups", []):
    print("-", question)