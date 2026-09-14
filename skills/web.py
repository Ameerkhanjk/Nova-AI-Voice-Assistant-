"""Web lookup skill (DuckDuckGo — free, no API key needed)."""
from ddgs import DDGS


def web_search(query: str) -> str:
    results = DDGS().text(query, max_results=4)
    if not results:
        return "No results found."
    return "\n".join(f"- {r['title']}: {r['body'][:200]}" for r in results)
