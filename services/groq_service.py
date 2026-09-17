"""
Groq-powered fallback synthesis for NewsLens AI.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from config import MAX_CONTENT_LENGTH, MAX_OUTPUT_TOKENS
from utils.text_utils import format_sources_block


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# We can change this model later if needed.
GROQ_MODEL = "openai/gpt-oss-120b"


# ---------------------------------------------------------
# Groq client
# ---------------------------------------------------------

_client = None


def _get_client() -> Groq:
    """
    Create the Groq client only when required.
    """

    global _client

    if _client is None:

        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is missing. "
                "Add it to your .env file."
            )

        _client = Groq(
            api_key=GROQ_API_KEY
        )

    return _client


# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are NewsLens AI, a careful multilingual research assistant.

LANGUAGE RULE:
- Detect the language of the user's question.
- Answer in the SAME language as the user's question.
- English question → English answer.
- Hindi question → Hindi answer.
- Odia question → Odia answer.
- Bengali question → Bengali answer.
- Do not automatically translate the answer into English.
- Follow the user's language naturally.
- Keep source citations such as [1], [2] unchanged.

RESEARCH RULES:
- Base factual claims only on the numbered sources provided.
- Cite claims using [1], [2], [3], etc.
- Never invent facts, statistics, sources, or URLs.
- If sources disagree, clearly mention the disagreement.
- If the sources do not contain enough information, say so.
- Do not assume information that is not present in the sources.

QUALITY:
- Give a clear and useful answer.
- Match the requested research mode.
- Use natural language.
- Avoid unnecessary jargon.

FOLLOW-UP QUESTIONS:
After the main answer, output:

###FOLLOWUPS###

Then provide exactly 3 short follow-up questions.

The follow-up questions must also be written in the SAME LANGUAGE as the user's original question.
"""
# ---------------------------------------------------------
# Research modes
# ---------------------------------------------------------

MODE_INSTRUCTIONS = {
    "quick": """
Write a QUICK BRIEF.

Give 3-5 short paragraphs containing the most important information.

Answer in the SAME LANGUAGE as the user's question.
""",

    "deep": """
Write a DEEP RESEARCH report.

Use clear sections such as:

- What's Happening
- Background / Context
- Key Developments
- Different Perspectives or Disagreement
- Implications

Translate section headings naturally into the user's language.

Answer completely in the SAME LANGUAGE as the user's question.
""",

    "simple": """
EXPLAIN SIMPLY.

Use:
- short sentences
- everyday words
- simple explanations
- minimal jargon

Answer in the SAME LANGUAGE as the user's question.
""",
}

# ---------------------------------------------------------
# Generate research
# ---------------------------------------------------------

def run_research(
    query: str,
    mode: str,
    sources: list[dict],
) -> dict:
    """
    Generate a research response using Groq.

    Returns:

    {
        "analysis": "...",
        "follow_ups": [...]
    }
    """

    client = _get_client()

    # Prepare Tavily sources
    sources_block = format_sources_block(
        sources,
        MAX_CONTENT_LENGTH,
    )

    # Select research mode
    mode_instruction = MODE_INSTRUCTIONS.get(
        mode,
        MODE_INSTRUCTIONS["quick"],
    )

    # Build prompt
    user_prompt = f"""
User question:
{query}

Research mode:
{mode_instruction}

Numbered research sources:
{sources_block}

Analyze these sources and answer the user's question.

Remember:

- Use only the provided sources.
- Cite factual claims using [n].
- Do not invent information.
- Mention uncertainty or disagreement where relevant.
- End with exactly three follow-up questions.

Output the analysis first.

Then output:

###FOLLOWUPS###

1. ...
2. ...
3. ...
"""

    # Call Groq
    response = client.chat.completions.create(
        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        temperature=0.4,

        max_tokens=MAX_OUTPUT_TOKENS,
    )

    # Extract response
    text = response.choices[0].message.content or ""

    if not text:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    return _parse_response(text)


# ---------------------------------------------------------
# Parse response
# ---------------------------------------------------------

def _parse_response(text: str) -> dict:
    """
    Separate analysis and follow-up questions.
    """

    parts = text.split(
        "###FOLLOWUPS###",
        maxsplit=1,
    )

    analysis = parts[0].strip()

    follow_ups = []

    if len(parts) > 1:

        for line in parts[1].strip().splitlines():

            line = line.strip()

            if not line:
                continue

            # Remove numbering:
            # 1. question
            # 2. question
            # 3. question
            cleaned = line.lstrip(
                "0123456789.-) "
            ).strip()

            if cleaned:
                follow_ups.append(cleaned)

    return {
        "analysis": analysis,
        "follow_ups": follow_ups[:3],
    }


# ---------------------------------------------------------
# Test function
# ---------------------------------------------------------

def test_groq() -> str:
    """
    Simple Groq connection test.
    """

    client = _get_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Groq connection successful.",
            }
        ],
        temperature=0,
        max_tokens=20,
    )

    return response.choices[0].message.content.strip()