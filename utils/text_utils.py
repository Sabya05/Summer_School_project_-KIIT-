"""Small text-processing helpers shared by the services layer."""
import re


def clean_text(text: str) -> str:
    """Collapse whitespace and strip stray control characters from scraped web text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text.strip()


def truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


def dedupe_sources(sources: list[dict]) -> list[dict]:
    """Drop duplicate URLs / near-duplicate titles while preserving order."""
    seen_urls, seen_titles, unique = set(), set(), []
    for s in sources:
        url = (s.get("url") or "").strip().rstrip("/")
        title = (s.get("title") or "").strip().lower()
        if not url or url in seen_urls or title in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title)
        unique.append(s)
    return unique


def format_sources_block(sources: list[dict], max_content_len: int) -> str:
    """Turn source dicts into a numbered block Gemini can cite by [n]."""
    lines = []
    for i, s in enumerate(sources, start=1):
        content = truncate(clean_text(s.get("content", "")), max_content_len // max(len(sources), 1))
        lines.append(f"[{i}] {s.get('title', 'Untitled')}\nURL: {s.get('url', '')}\n{content}\n")
    return "\n".join(lines)


def domain_from_url(url: str) -> str:
    m = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else url or ""
