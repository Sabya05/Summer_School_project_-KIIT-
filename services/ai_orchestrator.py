"""
AI Orchestrator for NewsLens AI.

Primary AI:
    Gemini

Fallback AI:
    Groq

Flow:
    User Query
        ↓
    Tavily Sources
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


def run_ai_research(
    query: str,
    mode: str,
    sources: list[dict],
) -> dict:
    """
    Try Gemini first.

    If Gemini fails, try Groq as a fallback.

    Returns:
        {
            "analysis": "...",
            "follow_ups": [...],
            "provider": "Gemini" or "Groq"
        }
    """

    # =====================================================
    # 1. TRY GEMINI
    # =====================================================

    try:
        print("\n==============================")
        print("AI ORCHESTRATOR")
        print("==============================")
        print("Trying Gemini...")
        print(f"Query: {query}")
        print(f"Mode: {mode}")
        print(f"Sources: {len(sources)}")

        result = run_gemini(
            query=query,
            mode=mode,
            sources=sources,
        )

        result["provider"] = "Gemini"

        print("Gemini succeeded.")

        return result

    except Exception as gemini_error:

        print("\nGemini failed.")
        print(f"Gemini error: {gemini_error}")

    # =====================================================
    # 2. TRY GROQ
    # =====================================================

    try:
        print("\nSwitching to Groq...")
        print(f"Query: {query}")

        result = run_groq(
            query=query,
            mode=mode,
            sources=sources,
        )

        result["provider"] = "Groq"

        print("Groq succeeded.")

        return result

    except Exception as groq_error:

        print("\nGroq also failed.")
        print(f"Groq error: {groq_error}")

        # =================================================
        # 3. BOTH FAILED
        # =================================================

        raise RuntimeError(
            "Both AI providers failed.\n\n"
            f"Gemini error: {gemini_error}\n\n"
            f"Groq error: {groq_error}"
        ) from groq_error