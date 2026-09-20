"""
AI Orchestrator for NewsLens AI.

Flow:
    User Query
        ↓
    Tavily Sources
        ↓
    RAG Retrieval
        ↓
    Relevant Context
        ↓
    Gemini
        ↓
    Success → return Gemini response
        ↓
    Failure
        ↓
    Groq fallback
        ↓
    Success → return Groq response
"""

from services.gemini_service import run_research as run_gemini
from services.groq_service import run_research as run_groq
from rag.rag_pipeline import run_rag


def run_ai_research(
    query: str,
    mode: str,
    sources: list[dict],
) -> dict:

    print("\n==============================")
    print("AI ORCHESTRATOR")
    print("==============================")

    print("Original Tavily sources:", len(sources))
    print("Running RAG retrieval...")

    # ---------------------------------
    # 1. RAG RETRIEVAL
    # ---------------------------------

    try:

        relevant_sources = run_rag(
            query=query,
            sources=sources,
            k=5,
        )

        print(
            "RAG retrieved sources:",
            len(relevant_sources),
        )

    except Exception as rag_error:

        print("\nRAG failed.")
        print("RAG error:", rag_error)

        # If RAG fails, keep the application usable
        # by falling back to the original Tavily sources.
        relevant_sources = sources

        print(
            "Using original Tavily sources as fallback."
        )

    # ---------------------------------
    # 2. GEMINI PRIMARY MODEL
    # ---------------------------------

    try:

        print("\nTrying Gemini...")
        raise RuntimeError("TEST: Simulated Gemini failure")

        result = run_gemini(
            query=query,
            mode=mode,
            sources=relevant_sources,
        )

        result["provider"] = "Gemini"
        result["rag_used"] = True

        print("Gemini succeeded.")

        return result

    except Exception as gemini_error:

        print("\nGemini failed.")
        print("Gemini error:", gemini_error)

    # ---------------------------------
    # 3. GROQ FALLBACK
    # ---------------------------------

    try:

        print("\nSwitching to Groq...")

        result = run_groq(
            query=query,
            mode=mode,
            sources=relevant_sources,
        )

        result["provider"] = "Groq"
        result["rag_used"] = True

        print("Groq succeeded.")

        return result

    except Exception as groq_error:

        print("\nGroq also failed.")
        print("Groq error:", groq_error)

        raise RuntimeError(
            "Both AI providers failed.\n\n"
            f"Gemini error: {gemini_error}\n\n"
            f"Groq error: {groq_error}"
        ) from groq_error