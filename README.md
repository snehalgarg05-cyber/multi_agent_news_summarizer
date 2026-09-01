# 📰 Multi-Agent AI News Summarizer

🚀 **Live Demo:** https://multi-agent-news-summarizer.onrender.com/

A production-grade multi-agent AI system that automatically fetches real news, categorizes it by topic, summarizes each section, and delivers a clean executive briefing — powered by **Groq's OpenAI-compatible GPT-4o 120B model** and orchestrated with **LangGraph**.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  🔍 Fetcher      │  → Calls NewsAPI, cleans & structures articles
│     Agent       │
└────────┬────────┘
         │
    [conditional edge: success / error?]
         │
    ┌────▼────────────┐
    │ 🗂️ Categorizer  │  → LLM assigns each article to a topic category
    │    Agent        │
    └────┬────────────┘
         │
    ┌────▼────────────┐
    │ ✍️ Summarizer   │  → Per-category abstractive summarization
    │    Agent        │
    └────┬────────────┘
         │
    ┌────▼────────────┐
    │ 🎨 Formatter    │  → Executive briefing + beautiful markdown
    │    Agent        │
    └────┬────────────┘
         │
    Streamlit UI
```

---

## How It Works

Type a topic like **"artificial intelligence"** and click Run:

1. **Fetcher Agent** calls NewsAPI (50,000+ sources - BBC, TechCrunch, Reuters) and fetches the latest 10 articles
2. **Categorizer Agent** sends all articles to the LLM in one batch call - it intelligently groups them by topic (AI & ML, Tech Business, Finance, etc.)
3. **Summarizer Agent** writes an abstractive summary for each category - Overview, Key Developments, and What This Means
4. **Formatter Agent** writes a 3-sentence executive briefing and assembles the full markdown output
5. **Streamlit UI** renders everything with stats, source links, and an agent processing log

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **LangGraph** | Agent graph orchestration - nodes, edges, shared state |
| **LangChain** | Clean LLM interface (ChatGroq, SystemMessage, HumanMessage) |
| **Groq + GPT-4o 120B** | Ultra-fast inference via Groq's LPU hardware |
| **NewsAPI** | Real-time news from 50,000+ sources |
| **Streamlit** | Python to web UI with zero HTML/CSS |
| **TypedDict** | Type-safe shared state between agents |
| **python-dotenv** | Secure API key management |

---

## Project Structure

```
multi_agent_news_summarizer/
├── app.py                    # Streamlit UI
├── pipeline.py               # LangGraph graph wiring
├── state.py                  # Shared AgentState TypedDict
├── agents/
│   ├── fetcher_agent.py      # NewsAPI → raw articles
│   ├── categorizer_agent.py  # LLM topic grouping
│   ├── summarizer_agent.py   # LLM summaries per category
│   └── formatter_agent.py    # Executive briefing + markdown
├── requirements.txt
└── .env                      # API keys (never committed)
```

---

## Key Engineering Decisions

**Batch Categorization** - All 10 articles categorized in 1 LLM call instead of 10 separate calls. Result: 10x fewer API calls, faster, cheaper.

**Conditional Edge** - After the Fetcher runs, LangGraph checks success/failure and routes to error handler automatically instead of crashing.

**Temperature Tuning** - Temperature 0 for categorization (deterministic), 0.3-0.4 for summaries (better prose quality).

**Abstractive Summarization** - LLM reads multiple articles and writes a new paragraph in its own words, not just copying sentences.

**Fallback Handling** - If LLM fails on one category, pipeline logs the error and continues. Never crashes on partial failure.

**Query Expansion** - "AI" expands to "artificial intelligence OR machine learning OR LLM" for better NewsAPI results.

---

## Setup & Run Locally

```bash
# Clone the repo
git clone https://github.com/snehalgarg05-cyber/multi_agent_news_summarizer
cd multi_agent_news_summarizer

# Install dependencies
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
# Add GROQ_API_KEY and NEWS_API_KEY to .env

# Run
streamlit run app.py
```

---

## State Flow

The same `AgentState` TypedDict gets richer at every step:

```
INITIAL   → { user_query, max_articles }
FETCHER   → + { raw_articles, fetch_status }
CATEGORIZER → + { categorized_articles }
SUMMARIZER  → + { summaries }
FORMATTER   → + { final_output }
```

---

## What I'd Improve Next

- **Streaming output** using `.astream()` so users see results as they generate
- **Map-Reduce** for 100+ articles to handle context window limits
- **User memory** to personalize briefings based on reading history
- **Daily email digest** scheduled every morning automatically
- **Source diversity scoring** to prevent over-representation from one outlet

---

## Author

**Snehal Garg** | VIT Bhopal | B.Tech CSE 2027
- LinkedIn: [linkedin.com/in/snehal-garg](https://linkedin.com/in/snehal-garg)
- GitHub: [github.com/snehalgarg05-cyber](https://github.com/snehalgarg05-cyber)
