"""Live web research via Tavily."""
from tavily import TavilyClient
from config import TAVILY_API_KEY, MAX_SEARCH_RESULTS
from utils.text_utils import dedupe_sources, clean_text


def get_client() -> TavilyClient:
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY is missing. Add it to your .env file.")
    return TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """Search the live web and return a clean, deduplicated list of {title, url, content}."""
    client = get_client()
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )

    sources = []
    for r in response.get("results", []):
        content = clean_text(r.get("content", ""))
        if not content:
            continue
        sources.append({
            "title": r.get("title") or "Untitled source",
            "url": r.get("url", ""),
            "content": content,
        })

    return dedupe_sources(sources)
