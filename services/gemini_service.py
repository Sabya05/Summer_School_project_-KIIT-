"""
Gemini-powered research synthesis for NewsLens AI.

Gemini is the primary AI provider.
Groq is handled separately as the fallback provider.
"""

import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import GEMINI_MODEL, MAX_CONTENT_LENGTH, MAX_OUTPUT_TOKENS
from utils.text_utils import format_sources_block


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

def _get_secret(key: str) -> str:
    """
    Get a secret from Streamlit Cloud secrets or local .env.
    """

    # Streamlit Cloud
    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets[key]

    except Exception:
        pass

    # Local .env / environment variable
    return os.getenv(key, "")


GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")

_client = None


# ============================================================
# GEMINI CLIENT
# ============================================================

def _get_client():
    """
    Create and reuse the Gemini client.
    """

    global _client

    if _client is None:

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file or Streamlit secrets."
            )

        _client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    return _client


# ============================================================
# SYSTEM PROMPT
# ============================================================

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
- Cite sources inline using [1], [2], [3], etc.
- Never invent facts, statistics, events, or sources.
- If sources disagree, clearly mention the disagreement.
- If the sources do not contain enough information, say so.
- Do not present unsupported assumptions as facts.
- Write clearly and naturally in the user's language.

IMPORTANT:
The retrieved context comes from a RAG pipeline.
Use the retrieved context as the primary evidence for your answer.

After the main answer, output:

###FOLLOWUPS###

Then provide exactly 3 short, numbered follow-up research questions in the SAME language as the user's question.
"""


# ============================================================
# RESEARCH MODE INSTRUCTIONS
# ============================================================

MODE_INSTRUCTIONS = {

    "quick": """
Write a QUICK BRIEF.

Use:
- 3-5 short paragraphs
- The most important facts
- Important recent developments
- Relevant citations

Keep the response concise.

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

Use citations throughout.

Write the entire response in the SAME LANGUAGE as the user's question.
""",

    "simple": """
EXPLAIN SIMPLY.

Use:
- Short sentences
- Everyday words
- Simple explanations
- Relevant examples when supported by the sources

Avoid unnecessary technical jargon.

Write in the SAME LANGUAGE as the user's question.
""",
}


# ============================================================
# ERROR HANDLING
# ============================================================

def _is_temporary_error(error: Exception) -> bool:
    """
    Check whether an error may be temporary and worth retrying.
    """

    message = str(error).upper()

    temporary_signals = [
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

    return any(
        signal in message
        for signal in temporary_signals
    )


# ============================================================
# GEMINI GENERATION WITH RETRY
# ============================================================

def _generate_with_retry(
    client,
    prompt: str,
    max_attempts: int = 3,
):
    """
    Generate a Gemini response with limited retry attempts.
    """

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                ),
            )

            return response

        except Exception as error:

            if not _is_temporary_error(error):
                raise

            if attempt == max_attempts - 1:
                raise

            wait_time = 2 ** attempt

            print(
                f"Gemini temporary error. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)


# ============================================================
# RESPONSE PARSER
# ============================================================

def _parse_response(text: str) -> dict:
    """
    Separate the main answer from the follow-up questions.
    """

    if not text:
        return {
            "answer": "",
            "followups": [],
        }

    # Normalize whitespace slightly
    text = text.strip()

    # Find follow-up section
    marker = "###FOLLOWUPS###"

    if marker in text:

        answer_part, followup_part = text.split(
            marker,
            1,
        )

    else:

        answer_part = text
        followup_part = ""

    answer = answer_part.strip()

    followups = []

    if followup_part:

        for line in followup_part.splitlines():

            line = line.strip()

            if not line:
                continue

            # Remove numbering:
            # 1. Question
            # 2) Question
            # 3 - Question
            cleaned = re.sub(
                r"^\s*\d+\s*[\.\)\-:]\s*",
                "",
                line,
            ).strip()

            if cleaned:
                followups.append(cleaned)

    # Ensure exactly three follow-ups when possible
    followups = followups[:3]

    return {
        "answer": answer,
        "followups": followups,
    }


# ============================================================
# MAIN RESEARCH FUNCTION
# ============================================================

def run_research(
    query: str,
    mode: str,
    sources: list[dict],
) -> dict:
    """
    Generate a research answer using Gemini.

    Sources are provided by Tavily + the RAG retrieval pipeline.
    """

    client = _get_client()

    # Format retrieved sources
    sources_block = format_sources_block(
        sources,
        MAX_CONTENT_LENGTH,
    )

    mode_instruction = MODE_INSTRUCTIONS.get(
        mode,
        MODE_INSTRUCTIONS["quick"],
    )

    prompt = f"""
USER QUESTION:
{query}


RESEARCH MODE:
{mode}


MODE INSTRUCTIONS:
{mode_instruction}


RETRIEVED SOURCES:
{sources_block}


TASK:
Answer the user's question using ONLY the retrieved sources above.

Follow the language rules and research rules from the system instructions.

Cite important factual statements using the source numbers.

Do not invent information.

At the end, output:

###FOLLOWUPS###

Then exactly 3 short follow-up questions.
"""

    # Generate response
    response = _generate_with_retry(
        client,
        prompt,
    )

    # --------------------------------------------------------
    # TEMPORARY DEBUGGING
    # --------------------------------------------------------

    try:
        text = response.text or ""

    except Exception:
        text = ""

    print("\n==============================")
    print("RAW GEMINI RESPONSE")
    print("==============================")
    print(repr(text))

    # --------------------------------------------------------
    # EMPTY RESPONSE CHECK
    # --------------------------------------------------------

    if not text.strip():
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # Parse response
    result = _parse_response(text)

    return result


# ============================================================
# GEMINI CONNECTION TEST
# ============================================================

def test_gemini() -> str:
    """
    Simple Gemini API test.
    """

    client = _get_client()

    response = _generate_with_retry(
        client,
        "Explain artificial intelligence in simple words.",
    )

    text = response.text or ""

    if not text.strip():
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text