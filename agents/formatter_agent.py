# ─────────────────────────────────────────────────────────────────
#  FORMATTER_AGENT.PY — Agent #4: The Presenter
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: Why a separate formatting agent?
#  -------------------------------------------
#  Formatting is NOT the summarizer's job. Single Responsibility
#  Principle — each agent does ONE thing.
#
#  The formatter:
#    - Takes all summaries
#    - Adds metadata (article count, sources, timestamps)
#    - Produces beautiful markdown for the UI
#    - Also uses LLM to write a "Daily Briefing" headline
#
#  CONCEPT: Final LLM call for "editorial intelligence"
#  -------------------------------------------------------
#  The formatter asks the LLM to write an executive briefing —
#  a 2-3 sentence "if you only had 30 seconds, here's what
#  happened today in the world" summary. This is the kind of
#  high-level synthesis that makes the product feel premium.
#
#  INPUT  → state["summaries"], state["user_query"]
#  OUTPUT → state["final_output"]
# ─────────────────────────────────────────────────────────────────

import os
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Category Emoji Map ────────────────────────────────────────────
CATEGORY_EMOJI = {
    "AI & Machine Learning":    "🤖",
    "Tech Business & Startups": "💼",
    "Cybersecurity":            "🔐",
    "Science & Space":          "🚀",
    "Health & Medicine":        "🏥",
    "Finance & Economy":        "📈",
    "Politics & Policy":        "🏛️",
    "Climate & Environment":    "🌍",
    "Sports":                   "⚽",
    "General News":             "📰",
}


def _generate_executive_briefing(summaries: list, query: str) -> str:
    """
    Use LLM to generate a high-level executive briefing.
    This is the "TL;DR of the TL;DRs" — ultra-compressed intelligence.
    """
    # Give the LLM category names + first lines of each summary
    categories_overview = ""
    for s in summaries[:5]:  # top 5 categories only
        first_line = s["summary"].split("\n")[0].replace("**Overview**", "").strip()
        categories_overview += f"• {s['category']}: {first_line[:200]}\n"

    response = llm.invoke([
        SystemMessage(content="You are a chief editor writing a daily executive briefing. Be crisp, insightful, and professional. Max 3 sentences."),
        HumanMessage(content=f"""Write a 3-sentence executive briefing for today's news about "{query}".

Top stories:
{categories_overview}

The briefing should feel like the opening of a premium newsletter — engaging, intelligent, to the point.""")
    ])

    return response.content.strip()


def format_output(state: dict) -> dict:
    """
    Agent #4 main function.
    Assembles the final markdown output for Streamlit to render.
    """
    print("🎨 [FormatterAgent] Formatting final output...")

    summaries   = state.get("summaries", [])
    user_query  = state.get("user_query", "today's news")
    steps       = state.get("processing_steps", [])
    today       = datetime.now().strftime("%B %d, %Y")
    total_arts  = sum(s.get("article_count", 0) for s in summaries)

    if not summaries:
        return {
            "final_output": "⚠️ No summaries available. Please try a different query.",
            "processing_steps": steps + ["⚠️ FormatterAgent: Nothing to format"]
        }

    # ── Executive Briefing ────────────────────────────────────────
    try:
        exec_briefing = _generate_executive_briefing(summaries, user_query)
    except Exception:
        exec_briefing = "Today's news digest is ready. Scroll down for category-wise summaries."

    # ── Build Markdown Output ─────────────────────────────────────
    # CONCEPT: f-strings for templating
    # We build the entire output as one big string.
    # Streamlit's st.markdown() will render this beautifully.

    output = f"""# 📰 Daily Intelligence Briefing
### {today} · Query: *{user_query}*

---

## 🎯 Executive Summary

> {exec_briefing}

---

**📊 Stats:** {total_arts} articles analyzed across {len(summaries)} categories

---

"""

    # ── Per-Category Sections ─────────────────────────────────────
    for summary in summaries:
        category    = summary["category"]
        emoji       = CATEGORY_EMOJI.get(category, "📌")
        art_count   = summary["article_count"]
        sources     = summary.get("sources", [])
        articles    = summary.get("articles", [])
        summary_txt = summary["summary"]

        output += f"## {emoji} {category}\n"
        output += f"*{art_count} articles · Sources: {', '.join(sources[:4])}*\n\n"
        output += f"{summary_txt}\n\n"

        # Add article links
        if articles:
            output += "**📎 Source Articles:**\n"
            for article in articles[:4]:  # max 4 links per category
                output += f"- [{article['title'][:80]}...]({article['url']}) — *{article['source']}*\n"

        output += "\n---\n\n"

    # ── Footer ────────────────────────────────────────────────────
    output += f"""
*🤖 Generated by Multi-Agent News Summarizer*
*Pipeline: FetcherAgent → CategorizerAgent → SummarizerAgent → FormatterAgent*
*Powered by LangGraph + Groq (Llama 3.3 70B)*
"""

    print("✅ [FormatterAgent] Output ready")

    return {
        "final_output": output,
        "processing_steps": steps + [
            f"✅ FormatterAgent: Final output ready ({len(output)} chars)"
        ]
    }