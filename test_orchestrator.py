from services.ai_orchestrator import run_ai_research


# Fake source for testing only
sources = [
    {
        "title": "Example Source",
        "url": "https://example.com",
        "content": (
            "Artificial intelligence is increasingly being "
            "used in software development and research."
        ),
    }
]


result = run_ai_research(
    query="What is the current role of AI in software development?",
    mode="quick",
    sources=sources,
)


print("\n==============================")
print("AI PROVIDER")
print("==============================")

print(result["provider"])


print("\n==============================")
print("ANALYSIS")
print("==============================")

print(result["analysis"])


print("\n==============================")
print("FOLLOW-UP QUESTIONS")
print("==============================")

for question in result["follow_ups"]:
    print("-", question)
    