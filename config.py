"""Central configuration for NewsLens AI. Loads secrets from .env — never hardcode keys."""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Preferred model — swap here only if Google deprecates it.
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

QUICK_TOPICS = ["AI & Technology", "World News", "Science", "Business", "Climate", "Cybersecurity"]
