"""
NewsLens AI — AI News Research & Summarization Assistant
Streamlit app: user query -> Tavily live search -> Gemini synthesis -> structured result.
"""
import streamlit as st
from pathlib import Path

from config import RESEARCH_MODES, QUICK_TOPICS, GEMINI_API_KEY, TAVILY_API_KEY
from services.tavily_service import search_web
from services.gemini_service import run_research
from utils.text_utils import domain_from_url, truncate

st.set_page_config(page_title="NewsLens AI", page_icon="✦", layout="wide")

# ---------- CSS ----------
css_path = Path(__file__).parent / "styles" / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------- state ----------
ss = st.session_state
ss.setdefault("mode", "deep")
ss.setdefault("query", "")
ss.setdefault("result", None)
ss.setdefault("pending_query", None)


def launch(q: str):
    ss.pending_query = q.strip()


# ---------- top nav ----------
nav_l, nav_r = st.columns([3, 1])
with nav_l:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px;'>"
        "✦ NewsLens AI</div>",
        unsafe_allow_html=True,
    )

# ---------- hero ----------
st.markdown('<div class="nl-hero nl-fade">', unsafe_allow_html=True)
st.markdown(
    '<div class="nl-badge"><span class="dot"></span>AI Powered Research</div>'
    '<div class="nl-title">Research the world.<br>Understand it <span class="grad">instantly.</span></div>'
    '<div class="nl-sub">Search the live web, analyze trusted sources and get clear, '
    'well-structured insights — powered by AI.</div>',
    unsafe_allow_html=True,
)

col_in, col_btn = st.columns([6, 1])
with col_in:
    query = st.text_input(
        "query", placeholder="What do you want to research? e.g. How is AI changing software engineering in 2026?",
        label_visibility="collapsed", value=ss.query,
    )
with col_btn:
    go = st.button("Research →", type="primary", use_container_width=True)

st.markdown('<div style="margin-top:14px;">', unsafe_allow_html=True)
topic_cols = st.columns(len(QUICK_TOPICS) + 1)
topic_cols[0].markdown('<span class="nl-pill" style="opacity:.6;">Quick Topics</span>', unsafe_allow_html=True)
for i, topic in enumerate(QUICK_TOPICS):
    if topic_cols[i + 1].button(topic, key=f"topic_{topic}"):
        ss.query = topic
        launch(topic)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="nl-stats">'
    '<div class="nl-stat"><span class="ic">🌐</span><div><b>Live Web</b><span>Real-time sources</span></div></div>'
    '<div class="nl-stat"><span class="ic">🧠</span><div><b>AI Analysis</b><span>Deep understanding</span></div></div>'
    '<div class="nl-stat"><span class="ic">🛡️</span><div><b>Trusted Sources</b><span>Verified information</span></div></div>'
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)  # close hero

if go and query.strip():
    ss.query = query
    launch(query)

# ---------- how it works ----------
st.markdown('<div class="nl-kicker">The Process</div><div class="nl-h2">How It Works</div>'
            '<div class="nl-sec-sub">From your question to clear insights — in just a few steps.</div>',
            unsafe_allow_html=True)
steps = [("01", "🔍", "Your Question"), ("02", "🌐", "Live Web Search"),
         ("03", "📄", "Source Analysis"), ("04", "✨", "AI Synthesis"), ("05", "✅", "Clear Research")]
cols = st.columns(5)
for c, (num, ic, lbl) in zip(cols, steps):
    c.markdown(
        f'<div class="nl-step"><div class="ring">{ic}</div><div class="num">{num}</div>'
        f'<div class="lbl">{lbl}</div></div>', unsafe_allow_html=True,
    )

st.markdown('<hr class="nl-div">', unsafe_allow_html=True)

# ---------- research modes ----------
st.markdown('<div class="nl-kicker">Research Modes</div><div class="nl-h2">Choose Your Research Mode</div>'
            '<div class="nl-sec-sub">Different goals. Different depth. Same powerful results.</div>',
            unsafe_allow_html=True)
mode_cols = st.columns(3)
for c, (key, m) in zip(mode_cols, RESEARCH_MODES.items()):
    active = "active" if ss.mode == key else ""
    with c:
        st.markdown(
            f'<div class="nl-mode {active}"><div class="ic">{m["icon"]}</div>'
            f'<div class="tag">{m["tag"]}</div><div class="title">{m["label"]}</div>'
            f'<div class="desc">{m["desc"]}</div></div>', unsafe_allow_html=True,
        )
        if st.button(f"Select {m['label']}", key=f"mode_{key}", use_container_width=True):
            ss.mode = key

st.markdown('<hr class="nl-div">', unsafe_allow_html=True)

# ---------- run pipeline ----------
if ss.pending_query:
    q = ss.pending_query
    ss.pending_query = None
    if not GEMINI_API_KEY or not TAVILY_API_KEY:
        st.error("Missing API keys. Add GEMINI_API_KEY and TAVILY_API_KEY to your .env file.")
    else:
        with st.spinner("Searching the live web and analyzing sources…"):
            try:
                sources = search_web(q)
                if not sources:
                    st.warning("No usable sources found for that query. Try rephrasing it.")
                else:
                    result = run_research(q, ss.mode, sources)
                    ss.result = {"query": q, "mode": ss.mode, "sources": sources, **result}
            except Exception as e:
                st.error(f"Research failed: {e}")

# ---------- results ----------
if ss.result:
    r = ss.result
    st.markdown('<div class="nl-kicker">Research In Action</div><div class="nl-h2">Research Result</div>'
                '<div class="nl-sec-sub">Beautifully organized. Easy to explore. Built for your curiosity.</div>',
                unsafe_allow_html=True)

    left, right = st.columns([2, 1])

    with left:
        st.markdown('<div class="nl-glass nl-result nl-fade">', unsafe_allow_html=True)
        mode_label = RESEARCH_MODES[r["mode"]]["label"]
        st.markdown(
            '<div class="status">✓ Research Complete</div>'
            f'<h3>{r["query"]}</h3>'
            f'<div class="meta"><span>🧭 Mode: {mode_label}</span>'
            f'<span>📚 Sources analyzed: {len(r["sources"])}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="nl-glass" style="padding:24px;margin-top:16px;">', unsafe_allow_html=True)
        st.markdown(r["analysis"])
        st.markdown("</div>", unsafe_allow_html=True)

        if r.get("follow_ups"):
            st.markdown('<div class="nl-glass" style="padding:20px;margin-top:16px;">'
                        '<b>✦ Continue Your Research</b><br>'
                        '<span style="color:var(--muted);font-size:13px;">Explore more angles, or dive deeper.</span>'
                        '</div>', unsafe_allow_html=True)
            fcols = st.columns(len(r["follow_ups"]))
            for c, fq in zip(fcols, r["follow_ups"]):
                if c.button(fq, key=f"fu_{fq[:24]}"):
                    launch(fq)
                    st.rerun()

    with right:
        st.markdown('<div class="nl-glass" style="padding:18px;"><b>🔗 Sources</b></div>', unsafe_allow_html=True)
        for i, s in enumerate(r["sources"], start=1):
            dom = domain_from_url(s["url"])
            snippet = truncate(s["content"], 110)
            st.markdown(
                f'<div class="nl-source"><div class="dom">{dom}</div>'
                f'<a href="{s["url"]}" target="_blank">[{i}] {s["title"]}</a>'
                f'<div class="snip">{snippet}</div></div>',
                unsafe_allow_html=True,
            )

st.markdown('<hr class="nl-div">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:var(--muted);font-size:12.5px;padding-bottom:20px;">'
    '✦ NewsLens AI &nbsp;·&nbsp; Live Web Research &nbsp;·&nbsp; Powered by Tavily &amp; Gemini</div>',
    unsafe_allow_html=True,
)
