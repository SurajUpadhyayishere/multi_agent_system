import streamlit as st
from dotenv import load_dotenv
import os
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from tools import web_search, scrape_url

load_dotenv()
api_key_mistral = os.getenv("MISTRAL_API_KEY")
api_key_tavily  = os.getenv("TAVILY_API_KEY")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UnfairTimeResearch — Know Anything. Instantly.",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;900&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Playfair+Display:wght@700;900&display=swap');

/* ─────────────────────────────────────────────────
   DESIGN TOKENS
───────────────────────────────────────────────── */
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

    /* spacing tokens — overridden per breakpoint */
    --page-px:   2.5rem;
    --hero-pt:   4.5rem;
    --hero-pb:   3rem;
    --h1-size:   clamp(3rem, 6.5vw, 5.5rem);
    --sub-size:  1.05rem;
    --card-px:   2.2rem;
    --card-py:   2rem;
}

/* ─────────────────────────────────────────────────
   BASE
───────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    color: var(--text);
}
.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 100% 60% at 10% -15%, rgba(99,102,241,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 70%  50% at 90% 105%, rgba(34,211,238,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 50%  40% at 50%  50%, rgba(129,140,248,0.04) 0%, transparent 70%);
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 var(--page-px) 5rem;
    max-width: 1240px;
    position: relative;
    z-index: 1;
    width: 100% !important;
    box-sizing: border-box;
}

/* ─────────────────────────────────────────────────
   LOGO BAR
───────────────────────────────────────────────── */
.logo-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.6rem 0 0;
    margin-bottom: 0.2rem;
    flex-wrap: wrap;
}
.logo-mark {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--violet2), var(--cyan));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
    box-shadow: 0 0 24px rgba(99,102,241,0.45), 0 0 60px rgba(34,211,238,0.12);
    flex-shrink: 0;
}
.logo-text {
    font-family: 'Outfit', sans-serif;
    font-weight: 700; font-size: 1.15rem; letter-spacing: -0.01em; color: var(--text);
}
.logo-text span {
    background: linear-gradient(90deg, var(--violet), var(--cyan));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.logo-badge {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--cyan);
    background: rgba(34,211,238,0.08); border: 1px solid rgba(34,211,238,0.2);
    padding: 0.25rem 0.7rem; border-radius: 20px; white-space: nowrap;
}

/* ─────────────────────────────────────────────────
   HERO
───────────────────────────────────────────────── */
.hero {
    padding: var(--hero-pt) 0 var(--hero-pb);
    text-align: left; max-width: 720px; position: relative;
}
.hero-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase;
    color: var(--violet); margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.hero-label::before {
    content: ''; width: 20px; height: 1px;
    background: var(--violet); display: inline-block; flex-shrink: 0;
}
.hero h1 {
    font-family: 'Outfit', sans-serif;
    font-weight: 900; font-size: var(--h1-size);
    line-height: 0.95; letter-spacing: -0.04em; color: var(--text); margin: 0 0 1.5rem;
}
.hero h1 .grad {
    background: linear-gradient(135deg, var(--violet) 0%, var(--cyan) 60%, var(--emerald) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-size: var(--sub-size); font-weight: 300;
    color: var(--muted2); line-height: 1.75; max-width: 480px;
}

/* ─────────────────────────────────────────────────
   DECORATIVE GRID
───────────────────────────────────────────────── */
.grid-deco {
    position: absolute; right: -100px; top: 40px;
    width: 340px; height: 340px; opacity: 0.06; pointer-events: none;
    background-image:
        linear-gradient(var(--violet) 1px, transparent 1px),
        linear-gradient(90deg, var(--violet) 1px, transparent 1px);
    background-size: 34px 34px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 80%);
}

/* ─────────────────────────────────────────────────
   RULER
───────────────────────────────────────────────── */
.ruler {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violet2), var(--cyan), transparent);
    margin: 0.5rem 0 2.5rem; opacity: 0.35;
}

/* ─────────────────────────────────────────────────
   INPUT CARD
───────────────────────────────────────────────── */
.input-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: var(--card-py) var(--card-px);
    position: relative; overflow: hidden;
    box-shadow: 0 0 60px rgba(99,102,241,0.06), inset 0 1px 0 rgba(255,255,255,0.04);
}
.input-wrap::after {
    content: ''; position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(129,140,248,0.5), transparent);
}
.input-glow {
    position: absolute; top: -80px; left: -80px; width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}

/* ─────────────────────────────────────────────────
   STREAMLIT COMPONENT OVERRIDES
───────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important; font-weight: 400 !important;
    padding: 0.85rem 1.1rem !important;
    transition: all 0.25s ease !important; caret-color: var(--cyan) !important;
    width: 100% !important; box-sizing: border-box !important;
    min-height: 48px !important; /* touch-friendly */
    -webkit-tap-highlight-color: transparent;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; font-weight: 300 !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--violet2) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15), 0 0 20px rgba(99,102,241,0.1) !important;
    background: rgba(99,102,241,0.04) !important; outline: none !important;
}
.stTextInput > label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important; letter-spacing: 0.2em !important;
    text-transform: uppercase !important; color: var(--violet) !important;
    font-weight: 400 !important; margin-bottom: 0.5rem !important;
}

/* ─────────────────────────────────────────────────
   BUTTON
───────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--violet2) 0%, #4f46e5 50%, #3730a3 100%) !important;
    color: #fff !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.95rem !important; letter-spacing: 0.02em !important;
    border: none !important; border-radius: 12px !important; padding: 0.8rem 2rem !important;
    cursor: pointer !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.4), 0 0 0 1px rgba(129,140,248,0.2) !important;
    width: 100% !important; min-height: 52px !important;
    -webkit-tap-highlight-color: transparent;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 36px rgba(99,102,241,0.5), 0 0 0 1px rgba(129,140,248,0.35) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.99) !important; }

/* ─────────────────────────────────────────────────
   PIPELINE
───────────────────────────────────────────────── */
.pipe-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 1.2rem; margin-top: 0.5rem;
}

/* ─────────────────────────────────────────────────
   STEP CARD
───────────────────────────────────────────────── */
.step-card {
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: 0.85rem;
    position: relative; overflow: hidden; transition: border-color 0.3s, box-shadow 0.3s;
}
.step-card.active {
    border-color: rgba(99,102,241,0.45); background: rgba(99,102,241,0.06);
    box-shadow: 0 0 32px rgba(99,102,241,0.1);
}
.step-card.done { border-color: rgba(52,211,153,0.3); background: rgba(52,211,153,0.04); }
.step-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: rgba(255,255,255,0.04); transition: background 0.3s;
}
.step-card.active::before { background: linear-gradient(to bottom, var(--violet), var(--cyan)); }
.step-card.done::before   { background: var(--emerald); }
.step-inner { display: flex; align-items: center; gap: 0.9rem; }
.step-icon {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center; font-size: 0.95rem;
    flex-shrink: 0; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.07);
    transition: all 0.3s;
}
.step-card.active .step-icon {
    background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.3);
    box-shadow: 0 0 12px rgba(99,102,241,0.2);
}
.step-card.done .step-icon { background: rgba(52,211,153,0.12); border-color: rgba(52,211,153,0.25); }
.step-body { flex: 1; min-width: 0; }
.step-name { font-size: 0.88rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.step-desc { font-size: 0.72rem; color: var(--muted); margin-top: 0.1rem; font-weight: 300; line-height: 1.4; }
.step-badge {
    font-family: 'Space Mono', monospace; font-size: 0.58rem; letter-spacing: 0.12em;
    padding: 0.2rem 0.5rem; border-radius: 20px; flex-shrink: 0; white-space: nowrap;
}
.badge-wait { color: var(--muted);   background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); }
.badge-run  { color: var(--violet);  background: rgba(99,102,241,0.12);  border: 1px solid rgba(99,102,241,0.25); }
.badge-done { color: var(--emerald); background: rgba(52,211,153,0.1);   border: 1px solid rgba(52,211,153,0.2);  }

/* ─────────────────────────────────────────────────
   CONNECTOR
───────────────────────────────────────────────── */
.step-connector {
    display: flex; justify-content: flex-start;
    padding-left: 2.2rem; margin: -0.4rem 0 0.4rem; position: relative; z-index: 0;
}
.connector-line {
    width: 1px; height: 14px;
    background: linear-gradient(to bottom, rgba(99,102,241,0.2), rgba(99,102,241,0.05));
}

/* ─────────────────────────────────────────────────
   STATS ROW
───────────────────────────────────────────────── */
.stats-row {
    display: flex; gap: 1px; background: var(--border2);
    border-radius: 12px; overflow: hidden; margin-top: 1.5rem; border: 1px solid var(--border2);
}
.stat-cell { flex: 1; background: var(--surface); padding: 0.9rem 1rem; text-align: center; }
.stat-val  { font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; color: var(--text); display: block; }
.stat-key  { font-family: 'Space Mono', monospace; font-size: 0.58rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin-top: 0.15rem; display: block; }

/* ─────────────────────────────────────────────────
   RESULTS
───────────────────────────────────────────────── */
.section-title { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; letter-spacing: -0.03em; color: var(--text); margin: 2.5rem 0 1.2rem; }
.result-card { background: var(--surface); border: 1px solid var(--border2); border-radius: 16px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }
.result-label {
    font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 0.9rem; padding-bottom: 0.7rem; border-bottom: 1px solid rgba(34,211,238,0.12);
    display: flex; align-items: center; gap: 0.5rem;
}
.result-text { font-size: 0.88rem; line-height: 1.85; color: var(--muted2); white-space: pre-wrap; font-family: 'Outfit', sans-serif; font-weight: 300; word-break: break-word; }
.report-card {
    background: var(--surface); border: 1px solid rgba(99,102,241,0.22); border-radius: 20px;
    padding: 2.2rem 2.5rem; margin-top: 1rem; position: relative; overflow: hidden;
    box-shadow: 0 0 60px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,0.04);
    word-break: break-word;
}
.report-card::after {
    content: ''; position: absolute; top: 0; left: 8%; right: 8%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.45), var(--cyan), transparent);
}
.report-label { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--violet); margin-bottom: 1.4rem; padding-bottom: 0.9rem; border-bottom: 1px solid rgba(99,102,241,0.15); }
.critic-card {
    background: var(--surface); border: 1px solid rgba(52,211,153,0.2); border-radius: 20px;
    padding: 2.2rem 2.5rem; margin-top: 1.2rem; position: relative; overflow: hidden;
    box-shadow: 0 0 50px rgba(52,211,153,0.05); word-break: break-word;
}
.critic-card::after {
    content: ''; position: absolute; top: 0; left: 8%; right: 8%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(52,211,153,0.4), transparent);
}
.critic-label { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--emerald); margin-bottom: 1.4rem; padding-bottom: 0.9rem; border-bottom: 1px solid rgba(52,211,153,0.15); }

/* ─────────────────────────────────────────────────
   DOWNLOAD BUTTON
───────────────────────────────────────────────── */
.stDownloadButton > button {
    background: transparent !important; color: var(--cyan) !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.72rem !important;
    font-weight: 400 !important; letter-spacing: 0.1em !important;
    border: 1px solid rgba(34,211,238,0.25) !important; border-radius: 8px !important;
    padding: 0.55rem 1.2rem !important; transition: all 0.2s !important;
    margin-top: 1rem !important; min-height: 44px !important; width: 100% !important;
}
.stDownloadButton > button:hover {
    border-color: var(--cyan) !important; background: rgba(34,211,238,0.06) !important;
    box-shadow: 0 0 16px rgba(34,211,238,0.15) !important;
}

/* ─────────────────────────────────────────────────
   MISC STREAMLIT
───────────────────────────────────────────────── */
.stSpinner > div { color: var(--violet) !important; }
.stAlert { background: rgba(251,113,133,0.08) !important; border: 1px solid rgba(251,113,133,0.2) !important; border-radius: 10px !important; color: var(--rose) !important; }
details { background: rgba(255,255,255,0.02) !important; border: 1px solid var(--border2) !important; border-radius: 12px !important; padding: 0.2rem !important; margin-bottom: 0.8rem !important; }
details summary {
    font-family: 'Space Mono', monospace !important; font-size: 0.7rem !important;
    color: var(--muted2) !important; letter-spacing: 0.1em !important;
    cursor: pointer; padding: 0.5rem !important;
    min-height: 44px; display: flex !important; align-items: center !important;
}
details summary:hover { color: var(--text) !important; }

/* ─────────────────────────────────────────────────
   FOOTER
───────────────────────────────────────────────── */
.footer {
    font-family: 'Space Mono', monospace; font-size: 0.6rem; color: var(--muted);
    text-align: center; margin-top: 5rem; letter-spacing: 0.15em; opacity: 0.5; line-height: 2;
}
.footer span { color: var(--violet); }

/* ─────────────────────────────────────────────────
   EXAMPLE CHIPS
───────────────────────────────────────────────── */
.example-chips { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; }
.chip-try { font-family: 'Space Mono', monospace; font-size: 0.6rem; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; }
.chip {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px; padding: 0.3rem 0.65rem; font-size: 0.74rem; color: var(--muted2);
    font-family: 'Outfit', sans-serif; font-weight: 300; transition: all 0.2s; cursor: default;
    min-height: 34px; display: inline-flex; align-items: center;
}
.chip:hover { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.2); color: var(--text); }

/* ─────────────────────────────────────────────────
   PIPELINE — HORIZONTAL SCROLL STRIP
   Used automatically on narrow viewports via CSS
───────────────────────────────────────────────── */
.pipeline-scroll {
    display: none;   /* shown only via media query below */
    gap: 0.7rem;
    overflow-x: auto;
    padding-bottom: 0.6rem;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}
.pipeline-scroll::-webkit-scrollbar { display: none; }
.pipeline-scroll .step-card {
    flex: 0 0 190px;
    margin-bottom: 0;
}
/* hide connectors inside the scroll strip */
.pipeline-scroll .step-connector { display: none; }

/* ═══════════════════════════════════════════════════
   BREAKPOINTS
════════════════════════════════════════════════════ */

/* ── LARGE DESKTOP ≥ 1400px ── */
@media (min-width: 1400px) {
    :root { --page-px: 3.5rem; --h1-size: clamp(4rem, 5.5vw, 6.2rem); }
    .block-container { max-width: 1400px; }
}

/* ── STANDARD DESKTOP 1024–1399px — DEFAULT, no overrides needed ── */

/* ── TABLET LANDSCAPE 768–1023px ── */
@media (min-width: 768px) and (max-width: 1023px) {
    :root {
        --page-px: 1.5rem; --hero-pt: 3rem; --hero-pb: 2rem;
        --h1-size: clamp(2.4rem, 5vw, 3.6rem); --sub-size: 0.97rem;
        --card-px: 1.6rem; --card-py: 1.6rem;
    }
    .block-container { padding: 0 var(--page-px) 3.5rem; }
    /* Stack Streamlit columns vertically */
    [data-testid="column"] { width: 100% !important; flex: none !important; min-width: 0 !important; }
    [data-testid="column"]:nth-child(2) { display: none !important; }   /* spacer */
    .hero { max-width: 100%; }
    .hero-sub { max-width: 100%; }
    .grid-deco { display: none; }
    /* Pipeline switches to horizontal scroll strip */
    .pipeline-scroll { display: flex; }
    /* hide vertical pipeline on tablet */
    .pipeline-vertical { display: none !important; }
    .step-desc { display: none; }
    .stats-row { margin-top: 1rem; }
    .report-card, .critic-card { padding: 1.6rem 1.8rem; }
}

/* ── TABLET PORTRAIT & LARGE PHONE 480–767px ── */
@media (min-width: 480px) and (max-width: 767px) {
    :root {
        --page-px: 1rem; --hero-pt: 2.2rem; --hero-pb: 1.5rem;
        --h1-size: clamp(2rem, 8vw, 2.8rem); --sub-size: 0.93rem;
        --card-px: 1.2rem; --card-py: 1.4rem;
    }
    .block-container { padding: 0 var(--page-px) 3rem; }
    [data-testid="column"] { width: 100% !important; flex: none !important; min-width: 0 !important; }
    [data-testid="column"]:nth-child(2) { display: none !important; }
    .hero { max-width: 100%; padding-bottom: 1.5rem; }
    .hero h1 { line-height: 1.0; margin-bottom: 1rem; }
    .hero-sub { max-width: 100%; }
    .grid-deco { display: none; }
    .logo-badge { font-size: 0.55rem; padding: 0.2rem 0.5rem; }
    /* Horizontal scroll pipeline */
    .pipeline-scroll { display: flex; }
    .pipeline-vertical { display: none !important; }
    .step-desc { display: none; }
    .report-card, .critic-card { padding: 1.4rem 1.2rem; }
    .result-card { padding: 1.2rem 1rem; }
    .section-title { font-size: 1.15rem; }
    .ruler { margin: 0.4rem 0 1.5rem; }
}

/* ── MOBILE ≤ 479px ── */
@media (max-width: 479px) {
    :root {
        --page-px: 0.75rem; --hero-pt: 1.8rem; --hero-pb: 1.2rem;
        --h1-size: clamp(1.8rem, 9vw, 2.4rem); --sub-size: 0.88rem;
        --card-px: 1rem; --card-py: 1.1rem;
    }
    .block-container { padding: 0 var(--page-px) 2.5rem; }
    /* Stack columns */
    [data-testid="column"] { width: 100% !important; flex: none !important; min-width: 0 !important; }
    [data-testid="column"]:nth-child(2) { display: none !important; }

    /* Logo */
    .logo-bar { padding-top: 1.1rem; gap: 0.5rem; }
    .logo-mark { width: 32px; height: 32px; font-size: 1rem; border-radius: 8px; }
    .logo-text { font-size: 0.95rem; }
    .logo-badge { font-size: 0.5rem; padding: 0.18rem 0.45rem; letter-spacing: 0.12em; }

    /* Hero */
    .hero { max-width: 100%; }
    .hero-label { font-size: 0.58rem; letter-spacing: 0.2em; }
    .hero h1 { line-height: 1.05; letter-spacing: -0.03em; margin-bottom: 0.9rem; }
    .hero-sub { max-width: 100%; line-height: 1.65; }
    .grid-deco { display: none; }
    .ruler { margin: 0.3rem 0 1.2rem; }

    /* Button — extra thumb-friendly */
    .stButton > button { min-height: 56px !important; font-size: 1rem !important; border-radius: 14px !important; }

    /* Chips — horizontal scroll on mobile */
    .example-chips { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 0.3rem; scrollbar-width: none; gap: 0.4rem; }
    .example-chips::-webkit-scrollbar { display: none; }
    .chip { flex-shrink: 0; font-size: 0.7rem; white-space: nowrap; }

    /* Pipeline: horizontal scroll strip */
    .pipeline-scroll { display: flex; }
    .pipeline-scroll .step-card { flex: 0 0 165px; padding: 0.9rem 0.9rem; }
    .pipeline-vertical { display: none !important; }
    .step-desc { display: none; }

    /* Stats */
    .stats-row { margin-top: 0.8rem; }
    .stat-val { font-size: 1rem; }
    .stat-key { font-size: 0.52rem; }

    /* Results */
    .section-title { font-size: 1.05rem; margin: 1.8rem 0 0.9rem; }
    .report-card, .critic-card { padding: 1.2rem 1rem; border-radius: 14px; }
    .result-card { padding: 1rem 0.9rem; border-radius: 12px; }
    .report-label, .critic-label, .result-label { font-size: 0.56rem; letter-spacing: 0.14em; }
    .stDownloadButton > button { font-size: 0.65rem !important; }
    .footer { font-size: 0.55rem; margin-top: 3rem; }
}

/* ─────────────────────────────────────────────────
   TOUCH DEVICES — disable hover transforms
───────────────────────────────────────────────── */
@media (hover: none) and (pointer: coarse) {
    .stButton > button:hover { transform: none !important; }
    .chip:hover { background: rgba(255,255,255,0.03); border-color: rgba(255,255,255,0.08); color: var(--muted2); }
}

/* ─────────────────────────────────────────────────
   REDUCED MOTION
───────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; animation: none !important; }
}
</style>
""", unsafe_allow_html=True)


# ── Helper: step card (vertical — desktop default) ────────────────────────────
ICONS = {"search": "⌖", "reader": "⟐", "writer": "✦", "critic": "◈"}
NAMES = {"search": "Search Agent", "reader": "Reader Agent", "writer": "Writer Chain", "critic": "Critic Chain"}
DESCS = {
    "search": "Hunts the freshest, highest-signal sources so you don't have to",
    "reader": "Dives deep into each source — extracting what actually matters",
    "writer": "Turns raw intel into a crisp, structured report you can act on",
    "critic": "Stress-tests the report for gaps, bias & accuracy before you see it",
}

def step_card(key: str, state: str):
    card_cls  = {"running": "active", "done": "done"}.get(state, "")
    badge_map = {"waiting": ("IDLE", "badge-wait"), "running": ("● LIVE", "badge-run"), "done": ("✓ DONE", "badge-done")}
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

def pipeline_scroll_strip(steps_list, get_state_fn):
    """Horizontal-scroll pipeline strip for tablet/mobile — rendered via HTML."""
    cards_html = ""
    for key in steps_list:
        state     = get_state_fn(key)
        card_cls  = {"running": "active", "done": "done"}.get(state, "")
        badge_map = {"waiting": ("IDLE", "badge-wait"), "running": ("● LIVE", "badge-run"), "done": ("✓ DONE", "badge-done")}
        badge_txt, badge_cls = badge_map.get(state, ("", ""))
        cards_html += f"""
        <div class="step-card {card_cls}" style="flex:0 0 190px;margin-bottom:0;">
            <div class="step-inner">
                <div class="step-icon">{ICONS[key]}</div>
                <div class="step-body"><div class="step-name">{NAMES[key]}</div></div>
                <span class="step-badge {badge_cls}">{badge_txt}</span>
            </div>
        </div>"""
    st.markdown(f'<div class="pipeline-scroll">{cards_html}</div>', unsafe_allow_html=True)


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
# Streamlit columns handle desktop side-by-side.
# CSS media queries above collapse them to single-column on ≤ 1023 px.
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

    r     = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]

    def get_state(step):
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    # ── Vertical pipeline (desktop) — CSS hides this on narrow screens ──
    st.markdown('<div class="pipeline-vertical">', unsafe_allow_html=True)
    for i, step in enumerate(steps):
        step_card(step, get_state(step))
        if i < len(steps) - 1:
            connector()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Horizontal scroll strip (tablet / mobile) — CSS shows this on narrow screens ──
    pipeline_scroll_strip(steps, get_state)

    # Stats
    elapsed = round(time.time() - st.session_state.t_start, 1) if st.session_state.done else 0
    n_done  = len(r)
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
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done    = False
        st.session_state.t_start = time.time()
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
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
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
                f'<div class="result-card">'
                f'<div class="result-label">⌖ Raw Sources · Search Agent</div>'
                f'<div class="result-text">{r["search"]}</div>'
                f'</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("⟐  Show me what was scraped & extracted", expanded=False):
            st.markdown(
                f'<div class="result-card">'
                f'<div class="result-label">⟐ Deep Content · Reader Agent</div>'
                f'<div class="result-text">{r["reader"]}</div>'
                f'</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown(
            '<div class="report-card">'
            '<div class="report-label">✦ Your Research Report — Ready to Use</div>',
            unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Report — Keep it, share it, use it",
            data=r["writer"],
            file_name=f"unfairtime_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(
            '<div class="critic-card">'
            '<div class="critic-label">◈ Independent Quality Review — What the Critic Said</div>',
            unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    UnfairTimeResearch &nbsp;·&nbsp; <span>Know anything. Instantly.</span>
    &nbsp;·&nbsp; Built on LangChain &amp; Streamlit
</div>
""", unsafe_allow_html=True)