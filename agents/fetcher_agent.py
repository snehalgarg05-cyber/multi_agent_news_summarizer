# ─────────────────────────────────────────────────────────────────
#  FETCHER_AGENT.PY — Agent #1: The News Hunter
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What does this agent do?
#  ------------------------------------
#  This agent's ONLY job is to go to the internet, fetch real
#  news articles based on what the user asked, and return them
#  in a clean structured format.
#
#  It uses NewsAPI — a free service that gives us headlines from
#  50,000+ news sources (BBC, TechCrunch, Reuters, etc.)
#
#  CONCEPT: Why a separate agent just for fetching?
#  --------------------------------------------------
#  Separation of concerns. If fetching breaks, only this agent
#  fails — the others are unaffected. Easy to debug, easy to
#  swap (e.g., replace NewsAPI with RSS feeds tomorrow).
#
#  INPUT  → state["user_query"], state["max_articles"]
#  OUTPUT → state["raw_articles"], state["fetch_status"]
# ─────────────────────────────────────────────────────────────────

import os
import requests
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

load_dotenv()

# ── Constants ────────────────────────────────────────────────────
NEWS_API_KEY  = os.getenv("NEWS_API_KEY")
NEWS_API_URL  = "https://newsapi.org/v2/everything"
NEWSAPI_TOP   = "https://newsapi.org/v2/top-headlines"


def _build_search_query(user_query: str) -> str:
    """
    CONCEPT: Query Expansion
    -------------------------
    User might type "AI news" — but NewsAPI works better with
    specific keywords. We expand the query slightly for better
    results while keeping it relevant.
    """
    query_map = {
        "ai":           "artificial intelligence OR machine learning OR LLM",
        "tech":         "technology OR software OR startup",
        "crypto":       "cryptocurrency OR bitcoin OR blockchain",
        "climate":      "climate change OR environment OR sustainability",
        "health":       "healthcare OR medicine OR medical research",
        "finance":      "stock market OR economy OR finance OR investment",
        "politics":     "politics OR government OR election OR policy",
        "science":      "science OR research OR discovery OR space",
        "sports":       "sports OR football OR cricket OR olympics",
    }
    query_lower = user_query.lower()
    for key, expanded in query_map.items():
        if key in query_lower:
            return expanded
    # fallback — use the query as-is
    return user_query


def fetch_news(state: dict) -> dict:
    """
    Main fetcher function — called by LangGraph as Agent #1.

    CONCEPT: Why does this function take AND return the whole state?
    ----------------------------------------------------------------
    LangGraph passes the entire state dict to each agent function.
    The agent reads what it needs, does its work, and returns a
    PARTIAL dict with just the keys it updated. LangGraph then
    merges this back into the full state automatically.

    This is powerful — agents don't need to know about each other,
    they just read/write to the shared state.
    """
    print("🔍 [FetcherAgent] Starting news fetch...")

    user_query   = state.get("user_query", "technology")
    max_articles = state.get("max_articles", 10)
    steps        = state.get("processing_steps", [])

    if not NEWS_API_KEY:
        return {
            "raw_articles": [],
            "fetch_status": "error: NEWS_API_KEY not set in .env",
            "error": "Missing NEWS_API_KEY",
            "processing_steps": steps + ["❌ FetcherAgent: API key missing"]
        }

    search_query = _build_search_query(user_query)

    # ── API Call ─────────────────────────────────────────────────
    # We look for news from the last 7 days
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    params = {
        "q":          search_query,
        "from":       from_date,
        "sortBy":     "publishedAt",       # newest first
        "pageSize":   max_articles,
        "language":   "en",
        "apiKey":     NEWS_API_KEY,
    }

    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise ValueError(f"NewsAPI error: {data.get('message', 'Unknown')}")

        articles_raw = data.get("articles", [])

        # ── CONCEPT: Data Cleaning ────────────────────────────
        # Real-world APIs return messy data. We clean it:
        # - Remove articles with no title or description
        # - Remove "[Removed]" placeholder articles NewsAPI sometimes returns
        # - Normalize the structure to our Article TypedDict
        articles: List[dict] = []
        for a in articles_raw:
            title = a.get("title", "") or ""
            desc  = a.get("description", "") or ""

            if not title or title == "[Removed]":
                continue
            if not desc or desc == "[Removed]":
                continue

            articles.append({
                "title":        title.strip(),
                "description":  desc.strip(),
                "url":          a.get("url", ""),
                "source":       a.get("source", {}).get("name", "Unknown"),
                "published_at": a.get("publishedAt", "")[:10],  # just the date
                "full_content": a.get("content", None),
            })

        if not articles:
            return {
                "raw_articles":    [],
                "fetch_status":    "error: no articles found for this query",
                "error":           "No articles returned",
                "processing_steps": steps + [f"⚠️ FetcherAgent: No articles for '{user_query}'"]
            }

        print(f"✅ [FetcherAgent] Fetched {len(articles)} articles")

        return {
            "raw_articles":    articles,
            "fetch_status":    "success",
            "error":           None,
            "processing_steps": steps + [
                f"✅ FetcherAgent: Fetched {len(articles)} articles for '{user_query}'"
            ]
        }

    except requests.exceptions.Timeout:
        return {
            "raw_articles":    [],
            "fetch_status":    "error: request timed out",
            "error":           "Timeout",
            "processing_steps": steps + ["❌ FetcherAgent: Request timed out"]
        }
    except Exception as e:
        return {
            "raw_articles":    [],
            "fetch_status":    f"error: {str(e)}",
            "error":           str(e),
            "processing_steps": steps + [f"❌ FetcherAgent: {str(e)}"]
        }