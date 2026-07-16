# ─────────────────────────────────────────────────────────────────
#  PIPELINE.PY — The Orchestrator: LangGraph in Action
# ─────────────────────────────────────────────────────────────────
#
#  CONCEPT: What is LangGraph?
#  ----------------------------
#  LangGraph is a framework for building STATEFUL, MULTI-STEP
#  AI pipelines where you define:
#    - NODES: individual agent functions
#    - EDGES: connections between agents (who calls whom)
#    - STATE: shared memory flowing through the graph
#
#  Think of it like a flowchart where each box is an AI agent.
#
#  CONCEPT: Why LangGraph over plain Python?
#  ------------------------------------------
#  You COULD call each agent function manually:
#    state = fetch_news(state)
#    state = categorize_articles(state)
#    state = summarize_articles(state)
#    ...
#
#  But LangGraph gives you:
#    ✅ Automatic state merging
#    ✅ Conditional branching (if error → go to error handler)
#    ✅ Easy to add parallel execution later
#    ✅ Built-in visualization of the graph
#    ✅ Checkpointing (pause/resume long pipelines)
#
#  CONCEPT: Graph Structure
#  -------------------------
#  START → fetcher → [check error?] → categorizer → summarizer → formatter → END
#                           ↓
#                      error_handler → END
#
# ─────────────────────────────────────────────────────────────────

from langgraph.graph import StateGraph, END
from state import AgentState
from agents.fetcher_agent      import fetch_news
from agents.categorizer_agent  import categorize_articles
from agents.summarizer_agent   import summarize_articles
from agents.formatter_agent    import format_output


# ── Error Handler Node ────────────────────────────────────────────
def handle_error(state: AgentState) -> dict:
    """
    CONCEPT: Error nodes in LangGraph
    ----------------------------------
    Instead of crashing, we route to this node when something
    goes wrong. It produces a user-friendly error message.
    This is production-grade error handling in agentic systems.
    """
    error = state.get("error", "Unknown error")
    fetch_status = state.get("fetch_status", "")

    error_messages = {
        "Missing NEWS_API_KEY": "🔑 **API Key Missing!** Please add your NEWS_API_KEY to the .env file.\n\nGet a free key at: https://newsapi.org",
        "Timeout": "⏱️ **Request Timed Out.** NewsAPI took too long. Please try again.",
        "No articles returned": f"🔍 **No Articles Found** for your query.\n\nTry a different topic like: 'AI', 'technology', 'finance', or 'health'.",
    }

    user_message = error_messages.get(
        error,
        f"❌ **Something went wrong:** {fetch_status}\n\nPlease check your API keys and try again."
    )

    return {
        "final_output": user_message,
        "processing_steps": state.get("processing_steps", []) + [f"❌ Pipeline ended with error: {error}"]
    }


# ── Conditional Edge: Should we continue or handle error? ─────────
def should_continue(state: AgentState) -> str:
    """
    CONCEPT: Conditional Edges in LangGraph
    -----------------------------------------
    After the fetcher runs, we check: did it succeed?
    - If YES → move to categorizer (return "categorize")
    - If NO  → move to error handler (return "error")

    This is the "if/else" of graph-based AI systems.
    In complex systems, you can have many conditional branches
    based on LLM decisions (this is the basis of ReAct agents).
    """
    fetch_status = state.get("fetch_status", "")
    raw_articles = state.get("raw_articles", [])

    if fetch_status == "success" and len(raw_articles) > 0:
        return "categorize"
    else:
        return "error"


# ── Build the Graph ───────────────────────────────────────────────
def build_pipeline() -> StateGraph:
    """
    CONCEPT: Building a LangGraph StateGraph
    ------------------------------------------
    1. Create a graph with our state type
    2. Add nodes (agent functions)
    3. Add edges (connections)
    4. Set entry point
    5. Compile → returns a runnable pipeline
    """

    # Step 1: Initialize graph with our state schema
    graph = StateGraph(AgentState)

    # Step 2: Add nodes
    # Each node = (name, function)
    # The function must take state dict and return partial state dict
    graph.add_node("fetcher",      fetch_news)
    graph.add_node("categorizer",  categorize_articles)
    graph.add_node("summarizer",   summarize_articles)
    graph.add_node("formatter",    format_output)
    graph.add_node("error_handler", handle_error)

    # Step 3: Add edges
    # set_entry_point → which node runs first
    graph.set_entry_point("fetcher")

    # After fetcher: conditional branch
    graph.add_conditional_edges(
        "fetcher",           # from this node
        should_continue,     # call this function to decide
        {
            "categorize": "categorizer",   # if "categorize" → go to categorizer
            "error":      "error_handler", # if "error" → go to error handler
        }
    )

    # Linear flow after categorizer
    graph.add_edge("categorizer",   "summarizer")
    graph.add_edge("summarizer",    "formatter")
    graph.add_edge("formatter",     END)
    graph.add_edge("error_handler", END)

    # Step 4: Compile
    return graph.compile()


# ── Public API ────────────────────────────────────────────────────
def run_pipeline(user_query: str, max_articles: int = 10) -> AgentState:
    """
    Main entry point called by the Streamlit UI.

    CONCEPT: Initial State
    -----------------------
    We must provide ALL required keys upfront, even if empty.
    LangGraph merges agent outputs into this initial state.
    Think of it as creating the "baton" before the race starts.
    """
    pipeline = build_pipeline()

    initial_state: AgentState = {
        "user_query":           user_query,
        "max_articles":         max_articles,
        "raw_articles":         [],
        "fetch_status":         "",
        "categorized_articles": [],
        "summaries":            [],
        "final_output":         "",
        "error":                None,
        "processing_steps":     [],
    }

    # .invoke() runs the full pipeline synchronously
    # CONCEPT: For async/streaming UI, use .astream() instead
    final_state = pipeline.invoke(initial_state)
    return final_state