import streamlit as st
from dotenv import load_dotenv
import os 
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from tools import web_search, scrape_url



api_key_mistral = st.secrets["MISTRAL_API_KEY"]
api_key_tavily = st.secrets["TAVILY_API_KEY"]
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=" UnfairTimeResearch — Know Anything. Instantly.",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;900&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Playfair+Display:wght@700;900&display=swap');

:root {
    --bg:        #05060f;
    --bg2:       #090b18;
    --surface:   #0e1225;
    --surface2:  #131830;
    --border:    rgba(99,102,241,0.18);
    --border2:   rgba(99,102,241,0.08);
    --cyan:      #22d3ee;
    --violet:    #818cf8;
    --violet2:   #6366f1;
    --rose:      #fb7185;
    --emerald:   #34d399;
    --text:      #e2e8f4;
    --muted:     #64748b;
    --muted2:    #94a3b8;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 100% 60% at 10% -15%, rgba(99,102,241,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 90% 105%, rgba(34,211,238,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(129,140,248,0.04) 0%, transparent 70%);
}

/* ── noise grain overlay ── */
.stApp::before {
    content:'';
    position:fixed;
    inset:0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events:none;
    z-index:0;
    opacity:0.4;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 2.5rem 5rem;
    max-width: 1240px;
    position: relative;
    z-index: 1;
}

/* ── LOGO BAR ── */
.logo-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.6rem 0 0;
    margin-bottom: 0.2rem;
}
.logo-mark {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--violet2), var(--cyan));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    box-shadow: 0 0 24px rgba(99,102,241,0.45), 0 0 60px rgba(34,211,238,0.12);
    flex-shrink: 0;
}
.logo-text {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    letter-spacing: -0.01em;
    color: var(--text);
}
.logo-text span {
    background: linear-gradient(90deg, var(--violet), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.logo-badge {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cyan);
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.2);
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
}

/* ── HERO ── */
.hero {
    padding: 4.5rem 0 3rem;
    text-align: left;
    max-width: 720px;
    position: relative;
}
.hero-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--violet);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hero-label::before {
    content: '';
    width: 20px;
    height: 1px;
    background: var(--violet);
    display: inline-block;
}
.hero h1 {
    font-family: 'Outfit', sans-serif;
    font-weight: 900;
    font-size: clamp(3rem, 6.5vw, 5.5rem);
    line-height: 0.95;
    letter-spacing: -0.04em;
    color: var(--text);
    margin: 0 0 1.5rem;
}
.hero h1 .grad {
    background: linear-gradient(135deg, var(--violet) 0%, var(--cyan) 60%, var(--emerald) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: var(--muted2);
    line-height: 1.75;
    max-width: 480px;
}

/* ── decorative grid ── */
.grid-deco {
    position: absolute;
    right: -100px;
    top: 40px;
    width: 340px;
    height: 340px;
    opacity: 0.06;
    pointer-events: none;
    background-image:
        linear-gradient(var(--violet) 1px, transparent 1px),
        linear-gradient(90deg, var(--violet) 1px, transparent 1px);
    background-size: 34px 34px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 80%);
}

/* ── RULER LINE ── */
.ruler {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violet2), var(--cyan), transparent);
    margin: 0.5rem 0 2.5rem;
    opacity: 0.35;
}

/* ── INPUT SECTION ── */
.input-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 60px rgba(99,102,241,0.06), inset 0 1px 0 rgba(255,255,255,0.04);
}
.input-wrap::after {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(129,140,248,0.5), transparent);
}
.input-glow {
    position: absolute;
    top: -80px; left: -80px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    padding: 0.85rem 1.1rem !important;
    transition: all 0.25s ease !important;
    caret-color: var(--cyan) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--muted) !important;
    font-weight: 300 !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--violet2) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15), 0 0 20px rgba(99,102,241,0.1) !important;
    background: rgba(99,102,241,0.04) !important;
}
.stTextInput > label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--violet) !important;
    font-weight: 400 !important;
    margin-bottom: 0.5rem !important;
}

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, var(--violet2) 0%, #4f46e5 50%, #3730a3 100%) !important;
    color: #fff !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.4), 0 0 0 1px rgba(129,140,248,0.2) !important;
    width: 100%;
    position: relative;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 36px rgba(99,102,241,0.5), 0 0 0 1px rgba(129,140,248,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── PIPELINE ── */
.pipe-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1.2rem;
    margin-top: 0.5rem;
}

/* ── STEP CARD ── */
.step-card {
    background: var(--surface2);
    border: 1px solid var(--border2);
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.85rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.step-card.active {
    border-color: rgba(99,102,241,0.45);
    background: rgba(99,102,241,0.06);
    box-shadow: 0 0 32px rgba(99,102,241,0.1);
}
.step-card.done {
    border-color: rgba(52,211,153,0.3);
    background: rgba(52,211,153,0.04);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: rgba(255,255,255,0.04);
    transition: background 0.3s;
}
.step-card.active::before { background: linear-gradient(to bottom, var(--violet), var(--cyan)); }
.step-card.done::before   { background: var(--emerald); }

.step-inner {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}
.step-icon {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.07);
    transition: all 0.3s;
}
.step-card.active .step-icon {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 0 12px rgba(99,102,241,0.2);
}
.step-card.done .step-icon {
    background: rgba(52,211,153,0.12);
    border-color: rgba(52,211,153,0.25);
}
.step-body { flex: 1; min-width: 0; }
.step-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
}
.step-desc {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.1rem;
    font-weight: 300;
}
.step-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    padding: 0.2rem 0.5rem;
    border-radius: 20px;
    flex-shrink: 0;
}
.badge-wait    { color: var(--muted); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); }
.badge-run     { color: var(--violet); background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.25); }
.badge-done    { color: var(--emerald); background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); }

/* ── CONNECTOR between steps ── */
.step-connector {
    display: flex;
    justify-content: flex-start;
    padding-left: 2.2rem;
    margin: -0.4rem 0;
    margin-bottom: 0.4rem;
    position: relative;
    z-index: 0;
}
.connector-line {
    width: 1px;
    height: 14px;
    background: linear-gradient(to bottom, rgba(99,102,241,0.2), rgba(99,102,241,0.05));
}

/* ── STATS ROW ── */
.stats-row {
    display: flex;
    gap: 1px;
    background: var(--border2);
    border-radius: 12px;
    overflow: hidden;
    margin-top: 1.5rem;
    border: 1px solid var(--border2);
}
.stat-cell {
    flex: 1;
    background: var(--surface);
    padding: 0.9rem 1rem;
    text-align: center;
}
.stat-val {
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text);
    display: block;
}
.stat-key {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.15rem;
    display: block;
}

/* ── RESULT PANELS ── */
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text);
    margin: 2.5rem 0 1.2rem;
}

.result-card {
    background: var(--surface);
    border: 1px solid var(--border2);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}
.result-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 0.9rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(34,211,238,0.12);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.result-text {
    font-size: 0.88rem;
    line-height: 1.85;
    color: var(--muted2);
    white-space: pre-wrap;
    font-family: 'Outfit', sans-serif;
    font-weight: 300;
}

.report-card {
    background: var(--surface);
    border: 1px solid rgba(99,102,241,0.22);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 60px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,0.04);
}
.report-card::after {
    content: '';
    position: absolute;
    top: 0; left: 8%; right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.45), var(--cyan), transparent);
}
.report-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--violet);
    margin-bottom: 1.4rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid rgba(99,102,241,0.15);
}

.critic-card {
    background: var(--surface);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-top: 1.2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 50px rgba(52,211,153,0.05);
}
.critic-card::after {
    content: '';
    position: absolute;
    top: 0; left: 8%; right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(52,211,153,0.4), transparent);
}
.critic-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--emerald);
    margin-bottom: 1.4rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid rgba(52,211,153,0.15);
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--cyan) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.1em !important;
    border: 1px solid rgba(34,211,238,0.25) !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s !important;
    margin-top: 1rem !important;
}
.stDownloadButton > button:hover {
    border-color: var(--cyan) !important;
    background: rgba(34,211,238,0.06) !important;
    box-shadow: 0 0 16px rgba(34,211,238,0.15) !important;
}

/* ── SPINNER ── */
.stSpinner > div { color: var(--violet) !important; }

/* ── WARNING ── */
.stAlert {
    background: rgba(251,113,133,0.08) !important;
    border: 1px solid rgba(251,113,133,0.2) !important;
    border-radius: 10px !important;
    color: var(--rose) !important;
}

/* ── EXPANDER ── */
details {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    padding: 0.2rem !important;
    margin-bottom: 0.8rem !important;
}
details summary {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--muted2) !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
    padding: 0.5rem 0.5rem !important;
}
details summary:hover {
    color: var(--text) !important;
}

/* ── FOOTER ── */
.footer {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: var(--muted);
    text-align: center;
    margin-top: 5rem;
    letter-spacing: 0.15em;
    opacity: 0.5;
}
.footer span { color: var(--violet); }

/* ── EXAMPLES ── */
.example-chips {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.chip-try {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    color: var(--muted);
    text-transform: uppercase;
}
.chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 0.25rem 0.65rem;
    font-size: 0.74rem;
    color: var(--muted2);
    font-family: 'Outfit', sans-serif;
    font-weight: 300;
    transition: all 0.2s;
    cursor: default;
}
.chip:hover {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.2);
    color: var(--text);
}
</style>
""", unsafe_allow_html=True)


# ── Helper: step card ─────────────────────────────────────────────────────────
ICONS = {"search": "⌖", "reader": "⟐", "writer": "✦", "critic": "◈"}
NAMES = {"search": "Search Agent", "reader": "Reader Agent", "writer": "Writer Chain", "critic": "Critic Chain"}
DESCS = {
    "search": "Hunts the freshest, highest-signal sources so you don't have to",
    "reader": "Dives deep into each source — extracting what actually matters",
    "writer": "Turns raw intel into a crisp, structured report you can act on",
    "critic": "Stress-tests the report for gaps, bias & accuracy before you see it",
}

def step_card(key: str, state: str):
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    badge_map = {
        "waiting": ("IDLE",    "badge-wait"),
        "running": ("● LIVE",  "badge-run"),
        "done":    ("✓ DONE",  "badge-done"),
    }
    badge_txt, badge_cls = badge_map.get(state, ("", ""))
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-inner">
            <div class="step-icon">{ICONS[key]}</div>
            <div class="step-body">
                <div class="step-name">{NAMES[key]}</div>
                <div class="step-desc">{DESCS[key]}</div>
            </div>
            <span class="step-badge {badge_cls}">{badge_txt}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def connector():
    st.markdown('<div class="step-connector"><div class="connector-line"></div></div>', unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("results", {}), ("running", False), ("done", False), ("t_start", 0.0)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── LOGO BAR ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="logo-bar">
    <div class="logo-mark">◈</div>
    <div class="logo-text">UnfairTime<span>Research</span></div>
    <div class="logo-badge">4 Agents · 1 Click</div>
</div>
""", unsafe_allow_html=True)


# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="position:relative;">
    <div class="grid-deco"></div>
    <div class="hero">
        <div class="hero-label">Your unfair research advantage</div>
        <h1>Know more.<br><span class="grad">In seconds, not hours.</span></h1>
        <p class="hero-sub">
            While others are still opening tabs, you already have the answer.
            Type any topic. Get a cited, expert-level report — fully written,
            reviewed, and ready to use.
        </p>
    </div>
</div>
<div class="ruler"></div>
""", unsafe_allow_html=True)


# ── LAYOUT ────────────────────────────────────────────────────────────────────
col_left, col_gap, col_right = st.columns([5, 0.4, 3.8])

with col_left:
    st.markdown('<div class="input-wrap"><div class="input-glow"></div>', unsafe_allow_html=True)

    topic = st.text_input(
        "What do you need to know?",
        placeholder="e.g. How is AI changing drug discovery in 2025?",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Get My Report Now", use_container_width=True)

    st.markdown("""
    <div class="example-chips">
        <span class="chip-try">Popular →</span>
        <span class="chip">AI agents replacing jobs</span>
        <span class="chip">CRISPR cancer cures</span>
        <span class="chip">Fusion energy 2025</span>
        <span class="chip">AGI — how close?</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="pipe-title">What\'s happening right now</div>', unsafe_allow_html=True)

    r = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]

    def get_state(step):
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    for i, step in enumerate(steps):
        step_card(step, get_state(step))
        if i < len(steps) - 1:
            connector()

    # Stats row
    elapsed = round(time.time() - st.session_state.t_start, 1) if st.session_state.done else 0
    n_done = len(r)
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-cell">
            <span class="stat-val">{n_done}<span style="font-size:0.7rem;color:var(--muted)">/4</span></span>
            <span class="stat-key">Agents Finished</span>
        </div>
        <div class="stat-cell">
            <span class="stat-val">{elapsed if st.session_state.done else "—"}<span style="font-size:0.7rem;color:var(--muted)">{"s" if st.session_state.done else ""}</span></span>
            <span class="stat-key">Total Time Saved</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── RUN PIPELINE ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Don't leave it blank — your report is one question away.")
    else:
        st.session_state.results  = {}
        st.session_state.running  = True
        st.session_state.done     = False
        st.session_state.t_start  = time.time()
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results   = {}
    topic_val = st.session_state.topic_input

    with st.spinner("⌖  Scouting the web for the sharpest, most relevant sources…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({"messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]})
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("⟐  Reading between the lines — extracting the intel that counts…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({"messages": [("user",
            f"Based on the following search results about '{topic_val}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{results['search'][:800]}")]})
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("✦  Crafting your report — turning raw data into clear insight…"):
        research_combined = f"SEARCH RESULTS:\n{results['search']}\n\nDETAILED SCRAPED CONTENT:\n{results['reader']}"
        results["writer"] = writer_chain.invoke({"topic": topic_val, "research": research_combined})
        st.session_state.results = dict(results)

    with st.spinner("◈  Running quality control — fact-checking before it reaches you…"):
        results["critic"] = critic_chain.invoke({"report": results["writer"]})
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done    = True
    st.rerun()


# ── RESULTS ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="ruler" style="margin-top:2.5rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Report Is Ready</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("⌖  Show me what the Search Agent found", expanded=False):
            st.markdown(
                f'<div class="result-card"><div class="result-label">⌖ Raw Sources · Search Agent</div>'
                f'<div class="result-text">{r["search"]}</div></div>',
                unsafe_allow_html=True
            )

    if "reader" in r:
        with st.expander("⟐  Show me what was scraped & extracted", expanded=False):
            st.markdown(
                f'<div class="result-card"><div class="result-label">⟐ Deep Content · Reader Agent</div>'
                f'<div class="result-text">{r["reader"]}</div></div>',
                unsafe_allow_html=True
            )

    if "writer" in r:
        st.markdown('<div class="report-card"><div class="report-label">✦ Your Research Report — Ready to Use</div>', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Report — Keep it, share it, use it",
            data=r["writer"],
            file_name=f"nexus_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown('<div class="critic-card"><div class="critic-label">◈ Independent Quality Review — What the Critic Said</div>', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    UnfairTimeResearch &nbsp;·&nbsp; <span>Know anything. Instantly.</span> &nbsp;·&nbsp; Built on LangChain &amp; Streamlit
</div>
""", unsafe_allow_html=True)