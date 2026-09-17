"""
Gemini-powered synthesis of Tavily research results.

NewsLens AI:
Tavily retrieves current web information.
Gemini analyzes only the retrieved sources and creates the final synthesis.
"""

import os
import re
import time

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_CONTENT_LENGTH,
    MAX_OUTPUT_TOKENS,
)
from utils.text_utils import format_sources_block


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Secret helper
# ---------------------------------------------------------

def _get_secret(key: str) -> str:
    """
    Try Streamlit secrets first.
    If not available, fall back to environment variables.
    """

    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return os.getenv(key, "")


# Get API key safely
API_KEY = _get_secret("GEMINI_API_KEY") or GEMINI_API_KEY


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

_client = None


def _get_client() -> genai.Client:
    """
    Create the Gemini client only when it is actually needed.
    """

    global _client

    if _client is None:

        if not API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file."
            )

        _client = genai.Client(api_key=API_KEY)

    return _client


# ---------------------------------------------------------
# Research modes
# ---------------------------------------------------------

MODE_INSTRUCTIONS = {
    "quick": """
Write a QUICK BRIEF.
Use 3-5 short paragraphs.
Focus only on the most important facts.
Write in the SAME LANGUAGE as the user's question.
""",

    "deep": """
Write a DEEP RESEARCH report.

Use clear sections such as:
- What's Happening
- Background / Context
- Key Developments
- Different Perspectives or Disagreement
- Implications

Translate the section headings into the user's language when appropriate.

Write the entire response in the SAME LANGUAGE as the user's question.
""",

    "simple": """
EXPLAIN SIMPLY.
Use short sentences, everyday words, and simple explanations.
Avoid unnecessary jargon.
Write in the SAME LANGUAGE as the user's question.
""",
}


# ---------------------------------------------------------
# System instruction
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are NewsLens AI, a careful multilingual research assistant.

IMPORTANT LANGUAGE RULE:
- Detect the language of the user's question.
- Answer in the SAME language as the user's question.
- If the user asks in Hindi, answer in Hindi.
- If the user asks in Odia, answer in Odia.
- If the user asks in Bengali, answer in Bengali.
- If the user asks in English, answer in English.
- Do not automatically translate the answer into English.
- Source titles and URLs may remain in their original language.
- Keep citations like [1], [2] unchanged.

RESEARCH RULES:
- Base every factual claim ONLY on the numbered sources provided.
- Cite sources inline using [1], [2], etc.
- Never invent facts, statistics, or sources.
- If sources disagree, clearly mention the disagreement.
- If the sources do not contain enough information, say so.
- Write clearly and naturally in the user's language.

After the main answer, output:

###FOLLOWUPS###

Then provide exactly 3 short follow-up research questions in the SAME language as the user's question.
"""

# ---------------------------------------------------------
# Temporary error detection
# ---------------------------------------------------------

def _is_temporary_error(error: Exception) -> bool:
    """
    Identify errors where retrying may help.

    Examples:
    - 429 RESOURCE_EXHAUSTED
    - 503 UNAVAILABLE
    - 500 INTERNAL
    - 502
    - 504
    """

    error_text = str(error).upper()

    temporary_errors = [
        "429",
        "RESOURCE_EXHAUSTED",
        "503",
        "UNAVAILABLE",
        "500",
        "INTERNAL",
        "502",
        "504",
        "DEADLINE_EXCEEDED",
        "TIMEOUT",
    ]

    return any(code in error_text for code in temporary_errors)


# ---------------------------------------------------------
# Gemini generation with retry
# ---------------------------------------------------------

def _generate_with_retry(
    client: genai.Client,
    prompt: str,
    max_attempts: int = 3,
):
    """
    Call Gemini with limited exponential-backoff retries.

    Attempt 1 -> immediately
    Attempt 2 -> wait 2 seconds
    Attempt 3 -> wait 4 seconds

    This prevents the application from endlessly retrying.
    """

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    temperature=0.4,
                ),
            )

            return response

        except Exception as error:

            # Do not retry permanent errors such as
            # invalid API key, permission denied, bad request, etc.
            if not _is_temporary_error(error):
                raise

            # Last attempt -> give up
            if attempt == max_attempts - 1:
                raise

            # Exponential backoff:
            # attempt 0 -> 2 sec
            # attempt 1 -> 4 sec
            delay = 2 ** (attempt + 1)

            print(
                f"Gemini temporary error. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)


# ---------------------------------------------------------
# Main research function
# ---------------------------------------------------------

def run_research(
    query: str,
    mode: str,
    sources: list[dict],
) -> dict:
    """
    Send Tavily sources + user query to Gemini.

    Returns:

    {
        "analysis": "...",
        "follow_ups": [...]
    }
    """

    # Get Gemini client
    client = _get_client()

    # Prepare Tavily sources
    sources_block = format_sources_block(
        sources,
        MAX_CONTENT_LENGTH,
    )

    # Get requested research mode
    mode_instruction = MODE_INSTRUCTIONS.get(
        mode,
        MODE_INSTRUCTIONS["quick"],
    )

    # Build Gemini prompt
    user_prompt = f"""
User question:
{query}

Research mode:
{mode_instruction}

Numbered research sources:
{sources_block}

Now analyze the provided research material.

Remember:

- Use only the provided sources.
- Cite important factual claims with [n].
- Do not invent information.
- Clearly mention uncertainty or disagreement.
- Finish with exactly 3 useful follow-up questions.

Output the analysis first.

Then output:

###FOLLOWUPS###

1. ...
2. ...
3. ...
"""

    # Call Gemini with retry handling
    response = _generate_with_retry(
        client,
        user_prompt,
    )

    # Safely extract response text
    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response. "
            "Please try the research again."
        )

    return _parse_response(text)


# ---------------------------------------------------------
# Response parser
# ---------------------------------------------------------

def _parse_response(text: str) -> dict:
    """
    Split Gemini response into:

    analysis
    follow-up questions
    """

    parts = re.split(
        r"###FOLLOWUPS###",
        text,
        maxsplit=1,
    )

    analysis = parts[0].strip()

    follow_ups = []

    if len(parts) > 1:

        for line in parts[1].strip().splitlines():

            cleaned = re.sub(
                r"^\s*[\d\.\)\-\u2022]+\s*",
                "",
                line,
            ).strip()

            if cleaned:
                follow_ups.append(cleaned)

    return {
        "analysis": analysis,
        "follow_ups": follow_ups[:3],
    }


# ---------------------------------------------------------
# Simple Gemini connection test
# ---------------------------------------------------------

def test_gemini() -> str:
    """
    Simple function for testing whether Gemini is reachable.
    """

    client = _get_client()

    response = _generate_with_retry(
        client,
        "Reply with exactly: Gemini connection successful.",
    )

    return response.text.strip()