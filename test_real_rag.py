from services.tavily_service import search_web
from services.ai_orchestrator import run_ai_research


query = "What are the latest developments in artificial intelligence?"

print("\n==============================")
print("REAL NEWSLENS RAG TEST")
print("==============================")


# 1. Tavily
print("\nSearching live web with Tavily...")

sources = search_web(query)

print("Tavily sources:", len(sources))


# 2. RAG + AI
print("\nRunning RAG + AI...")

result = run_ai_research(
    query=query,
    mode="quick",
    sources=sources,
)


# 3. Output
print("\n==============================")
print("FINAL RESULT")
print("==============================")

print("Provider:", result.get("provider"))
print("RAG used:", result.get("rag_used"))

print("\nAnswer:")
print(result.get("answer", ""))

print("\nFollow-up Questions:")

for question in result.get("followups", []):
    print("-", question)