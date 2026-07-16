# ─────────────────────────────────────────────────────────────────
#  APP.PY — Streamlit UI
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What is Streamlit?
#  ----------------------------
#  Streamlit converts Python scripts into interactive web apps.
#  No HTML, no CSS, no JavaScript needed.
#  You write Python → it renders a beautiful web UI automatically.
#
#  CONCEPT: st.session_state
#  ---------------------------
#  Streamlit reruns the ENTIRE script on every interaction
#  (button click, slider change, etc.). session_state is a
#  dictionary that PERSISTS across reruns — like a mini-database
#  for your current browser session.
#
#  Run with: streamlit run app.py
# ─────────────────────────────────────────────────────────────────

import streamlit as st
import time
from pipeline import run_pipeline

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 Multi-Agent News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #0a0f1a 100%);
        color: #e0e0ff;
    }

    /* Cards */
    .news-card {
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }

    /* Step log */
    .step-log {
        background: rgba(0, 0, 0, 0.4);
        border-left: 3px solid #8b5cf6;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        font-family: 'Fira Code', monospace;
        font-size: 13px;
        margin: 4px 0;
        color: #a78bfa;
    }

    /* Metric boxes */
    .metric-box {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }

    /* Header gradient text */
    .gradient-text {
        background: linear-gradient(90deg, #8b5cf6, #ec4899, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Agent Control Panel")
    st.markdown("---")

    st.markdown("### 🔍 Search Settings")
    user_query = st.text_input(
        "News Topic",
        value="artificial intelligence",
        placeholder="e.g. AI, climate, finance...",
        help="What topic do you want news about?"
    )

    max_articles = st.slider(
        "Articles to Fetch",
        min_value=5,
        max_value=20,
        value=10,
        help="More articles = richer summaries but slower processing"
    )

    st.markdown("---")
    st.markdown("### 🧠 Pipeline Architecture")
    st.markdown("""
    ```
    START
      ↓
    🔍 Fetcher Agent
    (NewsAPI → real articles)
      ↓
    🗂️  Categorizer Agent
    (LLM → topic grouping)
      ↓
    ✍️  Summarizer Agent
    (LLM → per-category summary)
      ↓
    🎨 Formatter Agent
    (LLM → executive briefing)
      ↓
    END
    ```
    """)

    st.markdown("---")
    run_button = st.button(
        "🚀 Run Pipeline",
        type="primary",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("### ⚙️ Built With")
    st.markdown("""
    - 🦜 **LangChain** — LLM calls
    - 🕸️ **LangGraph** — Agent orchestration
    - ⚡ **Groq** — Ultra-fast inference
    - 🦙 **Llama 3.3 70B** — The AI brain
    - 📡 **NewsAPI** — Real-time news
    - 🎈 **Streamlit** — This UI
    """)


# ── Main Area ─────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align: center; background: linear-gradient(90deg, #8b5cf6, #ec4899, #00e5ff);
-webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;'>
📰 Multi-Agent News Summarizer
</h1>
<p style='text-align: center; color: #6366f1; font-size: 1rem;'>
Powered by LangGraph · 4 Specialized AI Agents · Real-Time News Intelligence
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ── How It Works (collapsed by default) ──────────────────────────
with st.expander("💡 How This Works — Click to Learn"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        **🔍 Agent 1: Fetcher**
        Calls NewsAPI to get real articles based on your query.
        Cleans and structures the raw data.
        """)
    with col2:
        st.markdown("""
        **🗂️ Agent 2: Categorizer**
        Sends all articles to Llama 3.3 70B.
        Groups them by topic intelligently.
        """)
    with col3:
        st.markdown("""
        **✍️ Agent 3: Summarizer**
        For each category, synthesizes all articles into one
        clear, insightful summary with key facts.
        """)
    with col4:
        st.markdown("""
        **🎨 Agent 4: Formatter**
        Writes an executive briefing.
        Assembles the final beautiful output.
        """)

# ── Run Pipeline ──────────────────────────────────────────────────
if run_button:
    if not user_query.strip():
        st.error("Please enter a news topic!")
    else:
        # Progress display
        progress_container = st.empty()
        status_container   = st.empty()

        with progress_container.container():
            st.markdown("### ⚡ Pipeline Running...")
            progress_bar = st.progress(0)

            steps_display = st.empty()

            # ── Live status updates ───────────────────────────────
            status_msgs = [
                (0.10, "🔍 Agent 1/4: Fetching news from NewsAPI..."),
                (0.30, "🗂️  Agent 2/4: Categorizing articles with LLM..."),
                (0.55, "✍️  Agent 3/4: Generating intelligent summaries..."),
                (0.85, "🎨 Agent 4/4: Formatting executive briefing..."),
            ]

            # Show initial status
            status_container.info(status_msgs[0][1])

        # ── Actually run the pipeline ─────────────────────────────
        start_time = time.time()

        with st.spinner(""):
            try:
                result = run_pipeline(user_query, max_articles)
                success = True
            except Exception as e:
                result = {"final_output": f"❌ Unexpected error: {str(e)}", "processing_steps": []}
                success = False

        elapsed = round(time.time() - start_time, 1)

        # Clear progress UI
        progress_container.empty()
        status_container.empty()

        # ── Show Results ──────────────────────────────────────────
        if success and result.get("raw_articles"):

            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📰 Articles Fetched",  len(result.get("raw_articles", [])))
            with col2:
                st.metric("🗂️  Categories Found",  len(result.get("categorized_articles", [])))
            with col3:
                st.metric("✍️  Summaries Written", len(result.get("summaries", [])))
            with col4:
                st.metric("⏱️  Time Taken",        f"{elapsed}s")

            st.markdown("---")

        # Main output
        final_output = result.get("final_output", "No output generated.")
        st.markdown(final_output, unsafe_allow_html=False)

        # ── Agent Processing Log ──────────────────────────────────
        steps = result.get("processing_steps", [])
        if steps:
            st.markdown("---")
            with st.expander("🔬 Agent Processing Log — See exactly what each agent did"):
                for step in steps:
                    st.markdown(
                        f'<div class="step-log">{step}</div>',
                        unsafe_allow_html=True
                    )

        # ── Source Articles Table ─────────────────────────────────
        raw_articles = result.get("raw_articles", [])
        if raw_articles:
            with st.expander(f"📋 All {len(raw_articles)} Source Articles"):
                for i, article in enumerate(raw_articles, 1):
                    st.markdown(f"""
**{i}. [{article['title']}]({article['url']})**
*{article['source']} · {article['published_at']}*
{article['description']}
---""")

# ── Default State (before first run) ─────────────────────────────
else:
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px; color: #6366f1;'>
        <h2>👈 Configure your search in the sidebar</h2>
        <p style='font-size: 1.1rem;'>Enter a topic, set article count, and click <b>Run Pipeline</b></p>
        <br>
        <p style='color: #4c1d95;'>
        Try: <code>artificial intelligence</code> · <code>climate change</code> ·
        <code>cryptocurrency</code> · <code>space exploration</code>
        </p>
    </div>
    """, unsafe_allow_html=True)