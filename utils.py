"""Shared constants, CSS, helpers, and session state for PawPal+."""
import os
import logging
import streamlit as st
from dotenv import load_dotenv
from pawpal_system import Owner
from google import genai

load_dotenv()

logging.basicConfig(
    filename="pawpal.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

DATA_FILE  = "pawpal_data.json"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
gemini_client  = genai.Client(api_key=GEMINI_API_KEY)

SPECIES_EMOJI   = {"dog": "🐶", "cat": "🐱", "bird": "🐦", "rabbit": "🐰", "other": "🐾"}
PRIORITY_LABELS = {1: "Low", 2: "Med-Low", 3: "Medium", 4: "High", 5: "Critical"}
PRIORITY_COLORS = {1: "#16a34a", 2: "#0ea5e9", 3: "#ea580c", 4: "#dc2626", 5: "#7c3aed"}
STATUS_COLORS   = {"pending": "#0ea5e9", "completed": "#16a34a", "skipped": "#6b7280"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Keyframes ── */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 4px 14px rgba(14,165,233,0.40), inset 0 1px 0 rgba(255,255,255,0.20); }
    50%       { box-shadow: 0 4px 22px rgba(14,165,233,0.70), inset 0 1px 0 rgba(255,255,255,0.25); }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
}
@keyframes countUp {
    from { opacity: 0; transform: scale(0.85); }
    to   { opacity: 1; transform: scale(1); }
}

/* ── Base ── */
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* ── Hide chrome, keep sidebar toggle ── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebarNav"]  { display: none; }
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] { visibility: visible !important; display: flex !important; }

/* ── App background ── */
.stApp { background: #f0f7ff; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1080px; }

/* ─────────── SIDEBAR ─────────── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebarContent"] { padding: 1.4rem 1.2rem; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #cbd5e1; }

/* Sidebar save/load buttons */
[data-testid="stSidebar"] .stButton > button {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1.5px solid #334155 !important;
    box-shadow: none !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    padding: 8px 14px !important;
    border-radius: 8px !important;
    transform: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(14,165,233,0.12) !important;
    border-color: #0ea5e9 !important;
    color: #38bdf8 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Sidebar nav page links */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] button {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 10px 12px !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    text-decoration: none !important;
    transition: background 0.15s, color 0.15s !important;
    margin-bottom: 3px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
[data-testid="stSidebar"] [data-testid="stPageLink"] button:hover {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    transform: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] button {
    background: #0369a122 !important;
    color: #93c5fd !important;
    font-weight: 600 !important;
}

/* ─────────── GLOBAL TEXT ─────────── */
h1, h2, h3, h4 { color: #111827; line-height: 1.3; }
p, span         { color: #374151; }
.stMarkdown p   { color: #4b5563; font-size: 15px; line-height: 1.6; }
label           { color: #374151 !important; font-size: 13px !important; font-weight: 500 !important; }

/* ─────────── METRICS ─────────── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1.5px solid #bae6fd !important;
    border-top: 4px solid #0ea5e9 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 0 4px 16px rgba(14,165,233,0.10) !important;
    animation: fadeSlideUp 0.55s cubic-bezier(0.22,1,0.36,1) both !important;
    transition: box-shadow 0.2s, transform 0.2s !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 8px 24px rgba(14,165,233,0.18) !important;
    transform: translateY(-3px) !important;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 13px !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] {
    color: #075985 !important; font-size: 28px !important; font-weight: 700 !important;
    animation: countUp 0.6s cubic-bezier(0.22,1,0.36,1) both !important;
}

/* ─────────── BUTTONS ─────────── */
.stButton > button {
    background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 60%, #38bdf8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 11px 26px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.40), inset 0 1px 0 rgba(255,255,255,0.20) !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    position: relative !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #075985 0%, #0284c7 60%, #0ea5e9 100%) !important;
    box-shadow: 0 8px 24px rgba(14,165,233,0.50), inset 0 1px 0 rgba(255,255,255,0.25) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%) !important;
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.30) !important;
}
.stButton > button:focus-visible {
    outline: 3px solid #7dd3fc !important;
    outline-offset: 3px !important;
}

/* ─────────── INPUTS ─────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    color: #111827 !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #9ca3af !important; }

/* ─────────── TABS ─────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #f3f4f6;
    border-radius: 12px;
    padding: 4px;
    border: 1.5px solid #e5e7eb;
    gap: 2px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 8px 18px !important;
    transition: color 0.15s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #ffffff !important;
    color: #0284c7 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}

/* ─────────── EXPANDER ─────────── */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stExpander"] summary {
    color: #111827 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
}

/* ─────────── ALERTS ─────────── */
[data-testid="stAlert"] { border-radius: 12px !important; font-size: 14px !important; }

/* ─────────── CHAT ─────────── */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    padding: 4px !important;
}
[data-testid="stChatInput"] textarea { color: #111827 !important; font-size: 14px !important; }
[data-testid="stChatInput"] textarea:focus { border-color: #0ea5e9 !important; }

/* ─────────── DIVIDER ─────────── */
hr { border-color: #e5e7eb !important; margin: 28px 0 !important; }

/* ─────────── TOGGLE / CHECKBOX ─────────── */
.stToggle label, .stCheckbox label { color: #374151 !important; font-size: 14px !important; }

/* ─────────── SELECT SLIDER ─────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #0ea5e9 !important;
    border-color: #0ea5e9 !important;
}

/* ═══════════ CUSTOM COMPONENTS ═══════════ */

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 50%, #38bdf8 80%, #7dd3fc 100%);
    border-radius: 20px;
    padding: 42px 38px;
    margin-bottom: 28px;
    border: none;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(14,165,233,0.30);
    animation: fadeSlideDown 0.65s cubic-bezier(0.22,1,0.36,1) both;
}
.hero::after {
    content: "🐾";
    position: absolute; right: 36px; top: 50%;
    transform: translateY(-50%);
    font-size: 72px; opacity: 0.20;
    animation: float 4s ease-in-out infinite;
}
.hero h1 {
    font-size: 32px; font-weight: 700; color: #ffffff; margin: 0 0 6px;
    animation: fadeSlideDown 0.75s cubic-bezier(0.22,1,0.36,1) both;
}
.hero p  {
    font-size: 15px; color: #bae6fd; margin: 0; font-weight: 500;
    animation: fadeSlideDown 0.90s cubic-bezier(0.22,1,0.36,1) both;
}

/* Glass card (tinted) */
.glass-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1.5px solid #bae6fd;
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 14px;
    box-shadow: 0 4px 16px rgba(14,165,233,0.10);
    animation: fadeSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
}

/* White card */
.card {
    background: #ffffff;
    border: 1.5px solid #f0f9ff;
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(14,165,233,0.06);
    animation: fadeSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
}

/* Pet card */
.pet-card {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 100%);
    border: 1.5px solid #bae6fd;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    animation: fadeSlideUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
}
.pet-card:hover {
    box-shadow: 0 12px 32px rgba(14,165,233,0.22);
    transform: translateY(-5px) scale(1.01);
}
.pet-card .pet-emoji {
    font-size: 36px; display: block; margin-bottom: 8px;
    animation: float 3.5s ease-in-out infinite;
}
.pet-card h3 { margin: 0 0 3px; font-size: 17px; font-weight: 700; color: #075985; }
.pet-card p  { margin: 2px 0; font-size: 13px; color: #0284c7; }

/* Task card */
.task-card {
    display: flex; align-items: center; gap: 12px;
    padding: 13px 16px; border-radius: 12px; margin-bottom: 8px;
    background: #ffffff; border: 1.5px solid #f0f9ff;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    animation: fadeSlideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
}
.task-card:hover {
    border-color: #7dd3fc;
    box-shadow: 0 4px 16px rgba(14,165,233,0.15);
    transform: translateX(4px);
}
.task-name { flex: 1; font-weight: 600; font-size: 14px; color: #111827; }
.task-meta { font-size: 12px; color: #9ca3af; white-space: nowrap; }

/* Badge */
.badge {
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 99px;
    font-size: 11px; font-weight: 600;
    white-space: nowrap; border: 1px solid transparent;
    line-height: 1.6;
}

/* Typography helpers */
.section-label {
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #0ea5e9; margin-bottom: 10px;
}
.page-title { font-size: 28px; font-weight: 700; color: #075985; margin-bottom: 4px; line-height: 1.2; animation: fadeSlideDown 0.5s cubic-bezier(0.22,1,0.36,1) both; }
.page-sub   { font-size: 14px; color: #6b7280; margin-bottom: 24px; line-height: 1.5; animation: fadeIn 0.7s ease both; }

/* Progress bar */
.progress-track {
    background: #f0f9ff; border-radius: 99px; height: 8px; overflow: hidden; margin: 6px 0;
}
.progress-fill {
    height: 8px; border-radius: 99px;
    background: linear-gradient(90deg, #0ea5e9, #4ade80);
    transition: width 0.5s ease;
}

/* Timeline (Schedule page) */
.timeline-item {
    display: flex; gap: 14px; padding: 16px 0;
    border-bottom: 1px solid #f0f9ff;
    animation: fadeSlideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
    transition: background 0.2s;
}
.timeline-item:hover { background: #f0f9ff; border-radius: 12px; padding-left: 8px; }
.timeline-num {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #7dd3fc); color: white;
    font-weight: 700; font-size: 13px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(14,165,233,0.30);
    animation: pulse-glow 2.5s ease-in-out infinite;
}
.timeline-body { flex: 1; }
.timeline-name { font-weight: 600; font-size: 14px; color: #111827; }
.timeline-info { font-size: 12px; color: #9ca3af; margin-top: 3px; }

/* Chip buttons (AI page) */
/* Chip buttons — override ALL global button styles */
div.chip-btn .stButton > button,
div.chip-btn .stButton > button:hover,
div.chip-btn .stButton > button:active,
div.chip-btn .stButton > button:focus {
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 6px 14px !important;
    border-radius: 99px !important;
}
div.chip-btn .stButton > button {
    background: #f0f9ff !important;
    color: #0284c7 !important;
    border: 1.5px solid #bae6fd !important;
    box-shadow: none !important;
    transform: none !important;
}
div.chip-btn .stButton > button:hover {
    background: #e0f2fe !important;
    border-color: #0ea5e9 !important;
    color: #0369a1 !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.15) !important;
    transform: translateY(-1px) !important;
}

/* Stat bars */
.stat-row   { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.stat-label { font-size: 12px; color: #6b7280; width: 80px; flex-shrink: 0; }
.stat-bar   { flex: 1; background: #f0f9ff; border-radius: 99px; height: 5px; overflow: hidden; }
.stat-fill  { height: 5px; border-radius: 99px; background: #0ea5e9; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 99px; }

/* ── Accessibility: focus ring for all interactive elements ── */
a:focus-visible,
button:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid #93c5fd !important;
    outline-offset: 2px !important;
    border-radius: 6px;
}
/* High contrast text minimum */
.task-meta, .timeline-info { color: #6b7280 !important; } /* 4.6:1 on white */
</style>
"""


def init_state():
    for key, default in [
        ("owner", None), ("pets", {}),
        ("chat_messages", []), ("schedule_plan", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.owner is None and os.path.exists(DATA_FILE):
        owner = Owner.load_from_json(DATA_FILE)
        if owner:
            st.session_state.owner = owner
            st.session_state.pets  = {p.name: p for p in owner.pets}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_status():
    with st.sidebar:
        st.markdown(
            '<div style="padding:6px 0 18px">'
            '<p style="font-size:20px;font-weight:700;color:#f1f5f9;margin:0">🐾 PawPal+</p>'
            '<p style="font-size:12px;color:#64748b;margin:2px 0 0">AI Pet Care Scheduler</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.owner:
            all_t = st.session_state.owner.get_all_tasks() if st.session_state.pets else []
            done  = sum(1 for t in all_t if t.status == "completed")
            pct   = int(done / len(all_t) * 100) if all_t else 0
            st.markdown(
                f'<div style="background:#1e293b;border:1.5px solid #334155;'
                f'border-radius:12px;padding:14px;margin-bottom:16px">'
                f'<p style="font-size:11px;color:#64748b;margin:0 0 2px">Signed in as</p>'
                f'<p style="font-size:15px;font-weight:700;color:#e2e8f0;margin:0 0 10px">'
                f'{st.session_state.owner.name}</p>'
                f'<div class="progress-track">'
                f'<div class="progress-fill" style="width:{pct}%"></div></div>'
                f'<p style="font-size:11px;color:#64748b;margin:4px 0 0">'
                f'{done}/{len(all_t)} tasks · {pct}% done</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
            'color:#4ade80;text-transform:uppercase;margin:16px 0 8px">Pages</p>',
            unsafe_allow_html=True,
        )
        nav_items = [
            ("🏠", "Dashboard",    "app.py"),
            ("👤", "Owner & Pets", "pages/1_Owner_Pets.py"),
            ("📋", "Tasks",        "pages/2_Tasks.py"),
            ("📅", "Schedule",     "pages/3_Schedule.py"),
            ("🤖", "AI Assistant", "pages/4_AI_Assistant.py"),
        ]
        for icon, label, path in nav_items:
            st.page_link(path, label=f"{icon}  {label}", use_container_width=True)

        st.markdown(
            '<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
            'color:#4ade80;text-transform:uppercase;margin:16px 0 8px">Data</p>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save", use_container_width=True, key="g_save"):
                if st.session_state.owner and st.session_state.owner.save_to_json(DATA_FILE):
                    st.success("Saved!")
        with c2:
            if st.button("📂 Load", use_container_width=True, key="g_load"):
                if os.path.exists(DATA_FILE):
                    o = Owner.load_from_json(DATA_FILE)
                    if o:
                        st.session_state.owner = o
                        st.session_state.pets  = {p.name: p for p in o.pets}
                        st.rerun()


def priority_badge(p: int) -> str:
    color = PRIORITY_COLORS.get(p, "#6b7280")
    label = PRIORITY_LABELS.get(p, str(p))
    return (f'<span class="badge" style="background:{color}22;color:{color};'
            f'border:1px solid {color}44">{label}</span>')


def status_badge(s: str) -> str:
    icons  = {"pending": "⏳", "completed": "✅", "skipped": "⏭️"}
    color  = STATUS_COLORS.get(s, "#9ca3af")
    return (f'<span class="badge" style="background:{color}22;color:{color};'
            f'border:1px solid {color}44">{icons.get(s,"")} {s.capitalize()}</span>')


def render_task_list(tasks):
    if not tasks:
        st.markdown('<p style="color:#4b5563;font-size:14px;padding:12px 0">No tasks yet.</p>',
                    unsafe_allow_html=True)
        return
    for t in tasks:
        rec_icon = "🔄 " if t.recurring else ""
        time_str = f"🕐 {t.scheduled_time}" if t.scheduled_time else ""
        p_badge  = priority_badge(t.priority)
        s_badge  = status_badge(t.status)
        meta     = f"⏱ {t.duration_minutes} min" + (f" &nbsp;·&nbsp; {time_str}" if time_str else "")
        html = (
            f'<div class="task-card">'
            f'<span class="task-name">{rec_icon}{t.name}</span>'
            f'<span class="task-meta">{meta}</span>'
            f'{p_badge}'
            f'{s_badge}'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
