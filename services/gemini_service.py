"""Gemini-powered synthesis of Tavily research results."""
import re
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_CONTENT_LENGTH, MAX_OUTPUT_TOKENS
from utils.text_utils import format_sources_block

_client = None

MODE_INSTRUCTIONS = {
    "quick": (
        "Write a QUICK BRIEF: 3-5 short paragraphs max, covering only the most important "
        "facts a busy reader needs. Be direct and concise."
    ),
    "deep": (
        "Write a DEEP RESEARCH report with clear sections: What's Happening, Background/Context, "
        "Key Developments, Different Perspectives or Disagreement (if any), and Implications. "
        "Be thorough and specific, citing sources with [n] markers."
    ),
    "simple": (
        "EXPLAIN SIMPLY: use short sentences, everyday words, and light analogies. Avoid jargon. "
        "Assume the reader has no background in the topic."
    ),
}

SYSTEM_PROMPT = """You are NewsLens AI, a careful research assistant.
Rules:
- Base every claim ONLY on the numbered sources you are given. Cite sources inline like [1], [2].
- Never invent facts, statistics, or sources that are not in the provided material.
- If sources disagree or information is uncertain, say so explicitly.
- Write in clear, well-structured prose fit for a general audience.
- After the analysis, output a line "###FOLLOWUPS###" followed by exactly 3 short, numbered
  follow-up research questions a curious reader would want to ask next.
"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def run_research(query: str, mode: str, sources: list[dict]) -> dict:
    """Send sources + query to Gemini, return {'analysis': str, 'follow_ups': list[str]}."""
    client = _get_client()
    sources_block = format_sources_block(sources, MAX_CONTENT_LENGTH)
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["quick"])

    user_prompt = f"""User question: {query}

Research mode instruction: {mode_instruction}

Numbered sources:
{sources_block}

Now write the response, then the ###FOLLOWUPS### section as instructed."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.4,
        ),
    )

    text = response.text or ""
    return _parse_response(text)


def _parse_response(text: str) -> dict:
    parts = re.split(r"###FOLLOWUPS###", text, maxsplit=1)
    analysis = parts[0].strip()
    follow_ups = []
    if len(parts) > 1:
        for line in parts[1].strip().splitlines():
            cleaned = re.sub(r"^\s*[\d\.\)\-\u2022]+\s*", "", line).strip()
            if cleaned:
                follow_ups.append(cleaned)
    return {"analysis": analysis, "follow_ups": follow_ups[:3]}
