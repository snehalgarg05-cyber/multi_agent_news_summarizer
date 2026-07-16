# ─────────────────────────────────────────────────────────────────
#  CATEGORIZER_AGENT.PY — Agent #2: The Smart Sorter
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What is this agent doing?
#  ------------------------------------
#  This agent reads all the raw articles and groups them by topic.
#  It uses an LLM (Groq/Llama) to UNDERSTAND article content and
#  assign a category — not just keyword matching.
#
#  Example:
#    "OpenAI releases GPT-5 with 10x better reasoning" → "AI & LLMs"
#    "NVIDIA stock hits all-time high after AI chip demand" → "Tech Business"
#    "WHO warns about antibiotic resistance" → "Health & Medicine"
#
#  CONCEPT: Structured Output / JSON mode
#  ----------------------------------------
#  We tell the LLM: "respond ONLY in JSON format". This is called
#  structured output — instead of the LLM writing a paragraph,
#  it fills in a template we define. Critical for agentic systems
#  where one agent's output is another agent's input.
#
#  INPUT  → state["raw_articles"]
#  OUTPUT → state["categorized_articles"]
# ─────────────────────────────────────────────────────────────────

import os
import json
from collections import defaultdict
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────
# CONCEPT: Why Groq?
# Groq uses custom LPU (Language Processing Unit) hardware.
# Result: llama3-70b runs at ~800 tokens/second — 10x faster than
# OpenAI's API and completely FREE on the free tier.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,        # 0 = deterministic, consistent categorization
    api_key=os.getenv("GROQ_API_KEY")
)

# ── Predefined Categories ─────────────────────────────────────────
CATEGORIES = [
    "AI & Machine Learning",
    "Tech Business & Startups",
    "Cybersecurity",
    "Science & Space",
    "Health & Medicine",
    "Finance & Economy",
    "Politics & Policy",
    "Climate & Environment",
    "Sports",
    "General News",
]


def _categorize_batch(articles: list) -> dict:
    """
    CONCEPT: Batch Processing
    --------------------------
    Instead of calling the LLM once per article (expensive & slow),
    we send ALL articles in one prompt and ask the LLM to categorize
    all of them at once. This is called batching.

    One API call instead of N API calls = faster + cheaper.
    """

    # Build a numbered list of article titles + descriptions
    articles_text = ""
    for i, article in enumerate(articles):
        articles_text += f"{i}. TITLE: {article['title']}\n"
        articles_text += f"   DESC: {article['description'][:150]}\n\n"

    system_prompt = """You are a news categorization expert.
Your job is to categorize news articles into predefined categories.
You MUST respond with ONLY a valid JSON object — no explanation, no markdown, no extra text.
"""

    user_prompt = f"""Categorize each article below into one of these categories:
{chr(10).join(f'- {c}' for c in CATEGORIES)}

Articles:
{articles_text}

Respond with ONLY this JSON format:
{{
  "categorizations": [
    {{"index": 0, "category": "AI & Machine Learning"}},
    {{"index": 1, "category": "Finance & Economy"}},
    ...
  ]
}}

One entry per article. Use ONLY the exact category names listed above."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # ── CONCEPT: JSON Parsing with Error Handling ─────────────────
    # LLMs sometimes add extra text even when told not to.
    # We extract JSON robustly by finding the { } boundaries.
    raw = response.content.strip()

    # Find JSON boundaries
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"LLM didn't return valid JSON: {raw[:200]}")

    json_str = raw[start:end]
    data = json.loads(json_str)

    # Build index → category mapping
    result = {}
    for item in data.get("categorizations", []):
        idx = item.get("index")
        cat = item.get("category", "General News")
        # Validate category
        if cat not in CATEGORIES:
            cat = "General News"
        result[idx] = cat

    return result


def categorize_articles(state: dict) -> dict:
    """
    Agent #2 main function.

    CONCEPT: Why does categorization need an LLM?
    -----------------------------------------------
    Simple keyword matching fails:
    - "Apple releases new AI features" → is it "Tech" or "AI"?
    - "Fed raises rates amid AI investment boom" → "Finance" or "AI"?

    An LLM understands CONTEXT and NUANCE — it reads the whole
    title + description and makes a judgment call, just like a
    human editor would.
    """
    print("🗂️  [CategorizerAgent] Categorizing articles...")

    raw_articles = state.get("raw_articles", [])
    steps        = state.get("processing_steps", [])

    if not raw_articles:
        return {
            "categorized_articles": [],
            "processing_steps": steps + ["⚠️ CategorizerAgent: No articles to categorize"]
        }

    try:
        # Get category for each article from LLM
        index_to_category = _categorize_batch(raw_articles)

        # Group articles by category
        groups = defaultdict(list)
        for i, article in enumerate(raw_articles):
            category = index_to_category.get(i, "General News")
            groups[category].append(article)

        # Convert to list of CategoryGroup dicts
        categorized = []
        for category, articles in groups.items():
            categorized.append({
                "category": category,
                "articles": articles
            })

        # Sort: largest group first
        categorized.sort(key=lambda x: len(x["articles"]), reverse=True)

        category_summary = ", ".join(
            f"{g['category']}({len(g['articles'])})" for g in categorized
        )
        print(f"✅ [CategorizerAgent] Categories: {category_summary}")

        return {
            "categorized_articles": categorized,
            "processing_steps": steps + [
                f"✅ CategorizerAgent: Grouped into {len(categorized)} categories — {category_summary}"
            ]
        }

    except Exception as e:
        print(f"❌ [CategorizerAgent] Error: {e}")
        # Fallback: put everything in General News
        fallback = [{"category": "General News", "articles": raw_articles}]
        return {
            "categorized_articles": fallback,
            "processing_steps": steps + [f"⚠️ CategorizerAgent: LLM failed, fallback used — {str(e)}"]
        }