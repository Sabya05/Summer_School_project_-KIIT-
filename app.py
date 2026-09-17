"""
NewsLens AI
AI News Research & Summarization Assistant

Pipeline:
User Query
    ↓
Tavily Live Web Search
    ↓
Relevant Sources
    ↓
AI Orchestrator
    ├── Gemini
    └── Groq fallback
    ↓
Research Result
"""

import html
from pathlib import Path

import streamlit as st


from config import (
    RESEARCH_MODES,
    QUICK_TOPICS,
    TAVILY_API_KEY,
)

from services.tavily_service import search_web
from services.ai_orchestrator import run_ai_research

from utils.text_utils import (
    domain_from_url,
    truncate,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NewsLens AI",
    page_icon="✦",
    layout="wide",
)


# =========================================================
# LOAD CSS
# =========================================================

css_path = Path(__file__).parent / "styles" / "style.css"

if css_path.exists():
    st.markdown(
        f"""
        <style>
        {css_path.read_text(encoding="utf-8")}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SESSION STATE
# =========================================================

if "mode" not in st.session_state:
    st.session_state.mode = "deep"

if "query" not in st.session_state:
    st.session_state.query = ""

if "result" not in st.session_state:
    st.session_state.result = None

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# =========================================================
# HELPER
# =========================================================

def launch(query: str):
    """Queue a research query."""

    query = query.strip()

    if query:
        st.session_state.pending_query = query


# =========================================================
# BRAND
# =========================================================

st.html(
    """
    <div class="nl-brand">
        <span class="brand-star">✦</span>
        <span>NewsLens AI</span>
    </div>
    """
)


# =========================================================
# HERO
# =========================================================

st.html(
    """
    <div class="nl-hero nl-fade">

        <div class="nl-badge">
            <span class="dot"></span>
            AI Powered Research
        </div>

        <div class="nl-title">
            Research the world.<br>
            Understand it <span class="grad">instantly.</span>
        </div>

        <div class="nl-sub">
            Search the live web, analyze trusted sources and get
            clear, well-structured insights — powered by AI.
        </div>

    </div>
    """
)


# =========================================================
# SEARCH AREA
# =========================================================

input_col, button_col = st.columns([6, 1])


with input_col:

    query = st.text_input(
        "Research query",
        placeholder=(
            "What do you want to research? "
            "e.g. How is AI changing software engineering in 2026?"
        ),
        label_visibility="collapsed",
        value=st.session_state.query,
    )


with button_col:

    research_clicked = st.button(
        "Research →",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# QUICK TOPICS
# =========================================================

st.html(
    """
    <div class="nl-quick-label">
        QUICK TOPICS
    </div>
    """
)


topic_columns = st.columns(
    len(QUICK_TOPICS)
)


for i, topic in enumerate(QUICK_TOPICS):

    with topic_columns[i]:

        if st.button(
            topic,
            key=f"topic_{i}",
            use_container_width=True,
        ):

            st.session_state.query = topic
            launch(topic)


# =========================================================
# HERO STATS
# =========================================================

st.html(
    """
    <div class="nl-stats">

        <div class="nl-stat">

            <span class="ic">🌐</span>

            <div>
                <b>Live Web</b>
                <span>Real-time sources</span>
            </div>

        </div>


        <div class="nl-stat">

            <span class="ic">🧠</span>

            <div>
                <b>AI Analysis</b>
                <span>Deep understanding</span>
            </div>

        </div>


        <div class="nl-stat">

            <span class="ic">🛡️</span>

            <div>
                <b>Trusted Sources</b>
                <span>Source-backed research</span>
            </div>

        </div>

    </div>
    """
)


# =========================================================
# SEARCH BUTTON
# =========================================================

if research_clicked and query.strip():

    st.session_state.query = query.strip()

    launch(query)


# =========================================================
# HOW IT WORKS
# =========================================================

st.html(
    """
    <div class="nl-kicker">
        THE PROCESS
    </div>

    <div class="nl-h2">
        How It Works
    </div>

    <div class="nl-sec-sub">
        From your question to clear insights — in just a few steps.
    </div>
    """
)


steps = [
    ("01", "🔍", "Your Question"),
    ("02", "🌐", "Live Web Search"),
    ("03", "📄", "Source Analysis"),
    ("04", "✨", "AI Synthesis"),
    ("05", "✅", "Clear Research"),
]


step_columns = st.columns(5)


for column, (number, icon, label) in zip(
    step_columns,
    steps,
):

    with column:

        st.html(
            f"""
            <div class="nl-step">

                <div class="ring">
                    {icon}
                </div>

                <div class="num">
                    {number}
                </div>

                <div class="lbl">
                    {label}
                </div>

            </div>
            """
        )


st.html(
    '<hr class="nl-div">'
)


# =========================================================
# RESEARCH MODES
# =========================================================

st.html(
    """
    <div class="nl-kicker">
        RESEARCH MODES
    </div>

    <div class="nl-h2">
        Choose Your Research Mode
    </div>

    <div class="nl-sec-sub">
        Different goals. Different depth. Same powerful results.
    </div>
    """
)


mode_columns = st.columns(3)


for column, (key, mode) in zip(
    mode_columns,
    RESEARCH_MODES.items(),
):

    active = (
        "active"
        if st.session_state.mode == key
        else ""
    )

    with column:

        st.html(
            f"""
            <div class="nl-mode {active}">

                <div class="ic">
                    {mode["icon"]}
                </div>

                <div class="tag">
                    {mode["tag"]}
                </div>

                <div class="title">
                    {mode["label"]}
                </div>

                <div class="desc">
                    {mode["desc"]}
                </div>

            </div>
            """
        )


        if st.button(
            f"Select {mode['label']}",
            key=f"mode_{key}",
            use_container_width=True,
        ):

            st.session_state.mode = key
            st.rerun()


st.html(
    '<hr class="nl-div">'
)


# =========================================================
# RESEARCH PIPELINE
# =========================================================

if st.session_state.pending_query:

    research_query = (
        st.session_state.pending_query
    )

    st.session_state.pending_query = None


    # =====================================================
    # CHECK TAVILY
    # =====================================================

    if not TAVILY_API_KEY:

        st.error(
            "Missing TAVILY_API_KEY. "
            "Add it to your .env file."
        )


    else:

        with st.spinner(
            "Searching the live web and analyzing sources…"
        ):

            try:

                # ---------------------------------------------
                # TAVILY SEARCH
                # ---------------------------------------------

                sources = search_web(
                    research_query
                )


                if not sources:

                    st.warning(
                        "No usable sources were found. "
                        "Try rephrasing your question."
                    )


                else:

                    # -----------------------------------------
                    # AI ORCHESTRATOR
                    # -----------------------------------------

                    result = run_ai_research(
                        query=research_query,
                        mode=st.session_state.mode,
                        sources=sources,
                    )


                    # -----------------------------------------
                    # SAVE RESULT
                    # -----------------------------------------

                    st.session_state.result = {
                        "query": research_query,
                        "mode": st.session_state.mode,
                        "sources": sources,
                        **result,
                    }


            except Exception as error:

                st.error(
                    f"Research failed: {error}"
                )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.result:

    result = st.session_state.result


    # =====================================================
    # RESULT HEADING
    # =====================================================

    st.html(
        """
        <div class="nl-kicker">
            RESEARCH IN ACTION
        </div>

        <div class="nl-h2">
            Research Result
        </div>

        <div class="nl-sec-sub">
            Beautifully organized. Easy to explore.
            Built for your curiosity.
        </div>
        """
    )


    left_column, right_column = st.columns(
        [2, 1]
    )


    # =====================================================
    # LEFT COLUMN
    # =====================================================

    with left_column:

        mode_label = RESEARCH_MODES[
            result["mode"]
        ]["label"]


        provider = result.get(
            "provider",
            "AI",
        )


        safe_query = html.escape(
            result["query"]
        )


        # -------------------------------------------------
        # RESULT HEADER
        # -------------------------------------------------

        st.html(
            f"""
            <div class="nl-glass nl-result nl-fade">

                <div class="status">
                    ✓ Research Complete
                </div>

                <h3>
                    {safe_query}
                </h3>

                <div class="meta">

                    <span>
                        🧭 Mode: {mode_label}
                    </span>

                    <span>
                        📚 Sources analyzed:
                        {len(result["sources"])}
                    </span>

                    <span>
                        🤖 AI: {provider}
                    </span>

                </div>

            </div>
            """
        )


        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        st.markdown(
            '<div class="nl-glass result-analysis">',
            unsafe_allow_html=True,
        )


        st.markdown(
            result["analysis"]
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


        # -------------------------------------------------
        # FOLLOW-UP QUESTIONS
        # -------------------------------------------------

        if result.get("follow_ups"):

            st.html(
                """
                <div class="nl-glass nl-followup-box">

                    <b>
                        ✦ Continue Your Research
                    </b>

                    <div class="followup-sub">
                        Explore more angles, or dive deeper.
                    </div>

                </div>
                """
            )


            followup_columns = st.columns(
                len(result["follow_ups"])
            )


            for column, followup in zip(
                followup_columns,
                result["follow_ups"],
            ):

                with column:

                    if st.button(
                        followup,
                        key=f"followup_{followup[:30]}",
                        use_container_width=True,
                    ):

                        launch(followup)

                        st.rerun()


    # =====================================================
    # RIGHT COLUMN — SOURCES
    # =====================================================

    with right_column:

        st.html(
            """
            <div class="nl-glass sources-heading">
                <b>🔗 Sources</b>
            </div>
            """
        )


        for index, source in enumerate(
            result["sources"],
            start=1,
        ):

            url = source.get(
                "url",
                "#",
            )


            title = html.escape(
                source.get(
                    "title",
                    "Source",
                )
            )


            domain = html.escape(
                domain_from_url(url)
            )


            snippet = html.escape(
                truncate(
                    source.get(
                        "content",
                        "",
                    ),
                    110,
                )
            )


            st.html(
                f"""
                <div class="nl-source">

                    <div class="dom">
                        {domain}
                    </div>

                    <a href="{html.escape(url)}"
                       target="_blank"
                       rel="noopener noreferrer">

                        [{index}] {title}

                    </a>

                    <div class="snip">
                        {snippet}
                    </div>

                </div>
                """
            )


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <hr class="nl-div">

    <div class="nl-footer">
        ✦ NewsLens AI
        &nbsp;·&nbsp;
        Live Web Research
        &nbsp;·&nbsp;
        Powered by Tavily &amp; AI
    </div>
    """
)