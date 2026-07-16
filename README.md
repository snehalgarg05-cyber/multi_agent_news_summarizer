# 📰 Multi-Agent News Summarizer

> A production-grade AI system using **LangGraph multi-agent orchestration** to fetch, categorize, summarize, and present real-time news with intelligence.

![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4.8-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama3.3_70B-F55036?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 🏗️ Architecture

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

**Orchestrated by LangGraph StateGraph** — each agent reads from and writes to a shared `AgentState` TypedDict.

---

## 🚀 Features

- **4 Specialized AI Agents** — each with a single, focused responsibility
- **Real-time news** from 50,000+ sources via NewsAPI
- **LLM-powered categorization** — understands context, not just keywords
- **Abstractive summarization** — synthesizes multiple articles, not just copy-paste
- **Executive briefing** — 3-sentence "if you had 30 seconds" summary
- **Conditional routing** — graceful error handling in the pipeline
- **Beautiful Streamlit UI** — dark galaxy theme, live processing log

---

## 🧠 Concepts Demonstrated

| Concept | Where |
|---------|-------|
| LangGraph StateGraph | `pipeline.py` |
| Shared agent state (TypedDict) | `state.py` |
| Conditional edges / branching | `pipeline.py` → `should_continue()` |
| Structured LLM output (JSON mode) | `categorizer_agent.py` |
| Batch processing | `categorizer_agent.py` → `_categorize_batch()` |
| Abstractive summarization | `summarizer_agent.py` |
| Chain-of-thought prompting | `summarizer_agent.py` prompt |
| Error nodes in agent graphs | `pipeline.py` → `handle_error()` |
| Separation of concerns | One agent = one job |

---

## ⚙️ Setup

### 1. Clone & Install
```bash
git clone https://github.com/snehalgarg05-cyber/multi-agent-news-summarizer
cd multi-agent-news-summarizer
pip install -r requirements.txt
```

### 2. Get Free API Keys
- **Groq** (LLM): https://console.groq.com → Free tier, no credit card
- **NewsAPI**: https://newsapi.org → Free tier, 100 req/day

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
multi-agent-news-summarizer/
│
├── app.py                    # Streamlit UI
├── pipeline.py               # LangGraph orchestration
├── state.py                  # Shared AgentState TypedDict
├── requirements.txt
├── .env.example
│
└── agents/
    ├── fetcher_agent.py      # Agent 1: NewsAPI → structured articles
    ├── categorizer_agent.py  # Agent 2: LLM topic classification
    ├── summarizer_agent.py   # Agent 3: Per-category summarization
    └── formatter_agent.py    # Agent 4: Executive briefing + markdown
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph 0.4 |
| LLM Framework | LangChain 0.3 |
| LLM Model | Llama 3.3 70B via Groq |
| News Data | NewsAPI |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## 💡 Key Design Decisions

**Why LangGraph over plain Python?**
Conditional branching, automatic state merging, and easy extensibility. Adding a 5th agent requires just one `add_node` + `add_edge` call.

**Why Groq?**
800 tokens/second on Llama 3.3 70B — free tier, no billing. Ideal for projects and demos.

**Why separate Categorizer and Summarizer agents?**
Single responsibility. Mixing categorization logic into the summarizer creates prompt confusion and harder debugging.

**Why batch categorization?**
One API call for all articles instead of N calls = 10x faster, 10x cheaper in production.

---

## 🔮 Future Improvements

- [ ] Add streaming output (real-time token display)
- [ ] Implement Map-Reduce for 100+ article summarization
- [ ] Add memory across sessions (remember user preferences)
- [ ] Email digest feature (send summary to inbox)
- [ ] Deploy to Streamlit Cloud / HuggingFace Spaces

---

*Built by Snehal Garg · VIT Bhopal · B.Tech CSE 2027*