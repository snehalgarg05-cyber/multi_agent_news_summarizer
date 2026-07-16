# ─────────────────────────────────────────────────────────────────
#  SUMMARIZER_AGENT.PY — Agent #3: The Intelligence Extractor
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What is this agent doing?
#  ------------------------------------
#  For EACH category group, this agent:
#    1. Takes all article titles + descriptions
#    2. Asks the LLM to synthesize them into ONE coherent summary
#    3. Extracts key insights, trends, and important facts
#
#  This is the heart of the system — where raw news becomes
#  actual INTELLIGENCE.
#
#  CONCEPT: Summarization vs. Extraction
#  ----------------------------------------
#  Extraction = copy key sentences from articles (basic)
#  Summarization = understand + rewrite in your own words (what we do)
#
#  We're doing ABSTRACTIVE summarization — the LLM reads multiple
#  articles and writes a new paragraph that captures the big picture.
#  This is much harder (and more valuable) than just copying quotes.
#
#  CONCEPT: Chain of Thought Prompting
#  --------------------------------------
#  We structure our prompt to make the LLM "think" step by step:
#  1. What's the main story?
#  2. What are the key facts?
#  3. What's the trend/implication?
#  This produces much better summaries than just saying "summarize this".
#
#  INPUT  → state["categorized_articles"]
#  OUTPUT → state["summaries"]
# ─────────────────────────────────────────────────────────────────

import os
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,     # slight creativity for better writing
    api_key=os.getenv("GROQ_API_KEY")
)


def _summarize_category(category: str, articles: list) -> dict:
    """
    Summarize a single category of articles.

    CONCEPT: Context Window Management
    ------------------------------------
    LLMs have a "context window" — max text they can process at once.
    Llama3-70b on Groq has ~32k tokens. Each article ~100 tokens.
    So 10 articles = ~1000 tokens → safely within limits.

    For production systems with 100+ articles, you'd need to:
    - Chunk articles into batches
    - Summarize each batch
    - Then summarize the summaries (Map-Reduce pattern)
    """

    # Build article content for the prompt
    articles_content = ""
    for i, article in enumerate(articles, 1):
        articles_content += f"Article {i}: {article['title']}\n"
        articles_content += f"Source: {article['source']} | Date: {article['published_at']}\n"
        articles_content += f"Details: {article['description']}\n\n"

    system_prompt = """You are an expert news analyst and journalist.
You synthesize multiple news articles into clear, insightful summaries.
Your writing is concise, factual, and engaging.
Always cite sources when mentioning specific facts."""

    user_prompt = f"""Here are {len(articles)} news articles about "{category}":

{articles_content}

Write a comprehensive summary that:
1. Opens with the BIGGEST/most important story in 1-2 sentences
2. Covers KEY FACTS and developments (bullet points, 3-5 points)
3. Ends with a TREND or IMPLICATION — what does this mean going forward?

Format your response exactly like this:

**Overview**
[2-3 sentence overview of the main story]

**Key Developments**
• [fact 1 with source]
• [fact 2 with source]
• [fact 3 with source]
• [fact 4 if relevant]
• [fact 5 if relevant]

**What This Means**
[1-2 sentences on the broader trend or implication]"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return {
        "category":      category,
        "summary":       response.content.strip(),
        "article_count": len(articles),
        "sources":       list(set(a["source"] for a in articles)),
        "articles":      articles,   # keep originals for UI links
    }


def summarize_articles(state: dict) -> dict:
    """
    Agent #3 main function.
    Loops through each category and summarizes it.

    CONCEPT: Why loop instead of one big prompt?
    ---------------------------------------------
    Mixing 10 categories in one prompt causes "category bleeding" —
    the LLM starts mixing up which facts belong where.
    One prompt per category = clean, focused summaries.
    This is the "divide and conquer" pattern in agentic AI.
    """
    print("✍️  [SummarizerAgent] Generating summaries...")

    categorized = state.get("categorized_articles", [])
    steps       = state.get("processing_steps", [])

    if not categorized:
        return {
            "summaries": [],
            "processing_steps": steps + ["⚠️ SummarizerAgent: No categories to summarize"]
        }

    summaries = []
    for group in categorized:
        category = group["category"]
        articles = group["articles"]

        print(f"  → Summarizing '{category}' ({len(articles)} articles)...")

        try:
            summary = _summarize_category(category, articles)
            summaries.append(summary)
            print(f"  ✅ Done: '{category}'")
        except Exception as e:
            print(f"  ❌ Failed: '{category}' — {e}")
            # Add a fallback summary so pipeline doesn't break
            summaries.append({
                "category":      category,
                "summary":       f"Summary unavailable due to error: {str(e)}",
                "article_count": len(articles),
                "sources":       [],
                "articles":      articles,
            })

    print(f"✅ [SummarizerAgent] Generated {len(summaries)} summaries")

    return {
        "summaries": summaries,
        "processing_steps": steps + [
            f"✅ SummarizerAgent: Summarized {len(summaries)} categories"
        ]
    }