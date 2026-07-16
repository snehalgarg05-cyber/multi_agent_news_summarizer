# ─────────────────────────────────────────────────────────────────
#  STATE.PY — The Shared Memory of Our Multi-Agent System
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What is "State" in LangGraph?
#  ----------------------------------------
#  Imagine a relay race. Each runner (agent) gets a baton, does
#  their part, and passes it to the next runner. The baton is the
#  STATE — it carries all information between agents.
#
#  Every agent in our pipeline:
#    1. READS from state (what did the previous agent do?)
#    2. DOES its job
#    3. WRITES its output back to state (for the next agent)
#
#  TypedDict = a Python dict where each key has a defined type.
#  This prevents bugs — if an agent writes wrong data, Python warns.
# ─────────────────────────────────────────────────────────────────

from typing import TypedDict, List, Dict, Optional


class Article(TypedDict):
    """Represents a single news article fetched from NewsAPI."""
    title: str
    description: str
    url: str
    source: str
    published_at: str
    full_content: Optional[str]   # scraped full text (may be None)


class CategoryGroup(TypedDict):
    """A group of articles under one topic category."""
    category: str                 # e.g. "Artificial Intelligence"
    articles: List[Article]


class AgentState(TypedDict):
    """
    The master state object passed between all agents.

    Flow:
      user_query
        → [FetcherAgent]    fills: raw_articles, fetch_status
        → [CategorizerAgent] fills: categorized_articles
        → [SummarizerAgent]  fills: summaries
        → [FormatterAgent]   fills: final_output
    """
    # ── Input ──────────────────────────────────────────────────
    user_query: str               # e.g. "AI and technology news"
    max_articles: int             # how many articles to fetch

    # ── Fetcher Agent Output ───────────────────────────────────
    raw_articles: List[Article]   # list of fetched articles
    fetch_status: str             # "success" or "error: ..."

    # ── Categorizer Agent Output ───────────────────────────────
    categorized_articles: List[CategoryGroup]

    # ── Summarizer Agent Output ────────────────────────────────
    summaries: List[Dict]         # [{category, summary, article_count}]

    # ── Formatter Agent Output ─────────────────────────────────
    final_output: str             # beautiful markdown string for UI

    # ── Meta ───────────────────────────────────────────────────
    error: Optional[str]          # any pipeline error
    processing_steps: List[str]   # log of what each agent did