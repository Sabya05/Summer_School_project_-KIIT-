"""Central configuration for NewsLens AI.
Loads secrets from Streamlit Cloud secrets or local .env.
Never hardcode API keys.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str) -> str:
    """Get a secret from Streamlit Cloud or local environment."""

    # Try Streamlit Cloud secrets first
    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Fall back to local .env / environment variables
    return os.getenv(key, "")


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")
GROQ_API_KEY = get_secret("GROQ_API_KEY")


# Preferred Gemini model
GEMINI_MODEL = "gemini-3.5-flash"

MAX_SEARCH_RESULTS = 10
MAX_CONTENT_LENGTH = 12000
MAX_OUTPUT_TOKENS = 12000


RESEARCH_MODES = {
    "quick": {
        "label": "Quick Brief",
        "icon": "⚡",
        "tag": "FAST",
        "desc": "Get a concise overview of the topic with key points.",
    },
    "deep": {
        "label": "Deep Research",
        "icon": "◎",
        "tag": "DETAILED",
        "desc": "Multi-source investigation with comprehensive analysis.",
    },
    "simple": {
        "label": "Explain Simply",
        "icon": "💡",
        "tag": "EASY",
        "desc": "Complex topics explained in simple, clear language.",
    },
}


QUICK_TOPICS = [
    "AI & Technology",
    "World News",
    "Science",
    "Business",
    "Climate",
    "Cybersecurity",
]