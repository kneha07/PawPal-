import streamlit as st
from pawpal_system import Scheduler
from utils import inject_css, init_state, sidebar_status, priority_badge, PRIORITY_COLORS, PRIORITY_LABELS

st.set_page_config(page_title="PawPal+ | Schedule", page_icon="📅", layout="wide", initial_sidebar_state="expanded")
inject_css()
init_state()
sidebar_status()

st.markdown('<p class="section-label">Plan</p>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Daily Schedule</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Optimize your day around your pet care priorities</p>', unsafe_allow_html=True)

if not st.session_state.owner or not st.session_state.pets:
    st.warning("Set up owner and pets first.")
    st.stop()

all_tasks  = st.session_state.owner.get_all_tasks()
scheduler  = Scheduler(st.session_state.owner)
available  = st.session_state.owner.available_minutes
total_need = st.session_state.owner.get_total_required_minutes()

# ── Stats row ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Tasks",   len(all_tasks))
c2.metric("Time Needed",   f"{total_need} min")
c3.metric("Available",     f"{available} min")
c4.metric("Status",        "✅ Feasible" if scheduler.is_feasible() else "⚠️ Over budget")

# ── Conflicts ─────────────────────────────────────────────────────────────────
conflicts = scheduler.detect_conflicts(all_tasks)
if conflicts:
    for c in conflicts:
        st.warning(f"⚠️ {c}")
else:
    st.success("✅ No conflicts — schedule is clean.")

st.markdown("---")

# ── Generate button ───────────────────────────────────────────────────────────
col_text, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🎯 Generate Schedule", type="primary"):
        st.session_state.schedule_plan = scheduler.generate_plan()

plan = st.session_state.schedule_plan

if not plan:
    st.markdown(
        '<div class="card" style="text-align:center;padding:60px 20px">'
        '<p style="font-size:56px;margin:0">📅</p>'
        '<p style="color:#9ca3af;font-size:15px;margin-top:12px">'
        'Click <strong style="color:#0ea5e9">Generate</strong> to build your optimized daily plan</p>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    cumulative = 0
    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown('<p class="section-label">Optimized Timeline</p>', unsafe_allow_html=True)
        for i, t in enumerate(plan, 1):
            cumulative += t.duration_minutes
            pct = min(int(cumulative / available * 100), 100)
            color = PRIORITY_COLORS.get(t.priority, "#6366f1")
            time_str = f"@ {t.scheduled_time}" if t.scheduled_time else ""
            st.markdown(
                f"""<div class="timeline-item">
                    <div class="timeline-num" style="background:linear-gradient(135deg,{color},{color}aa)">{i}</div>
                    <div class="timeline-body">
                        <div class="timeline-name">{t.name}</div>
                        <div class="timeline-info">
                            ⏱ {t.duration_minutes} min &nbsp;·&nbsp;
                            {priority_badge(t.priority)} &nbsp;
                            {f'<span style="color:#64748b">{time_str}</span>' if time_str else ''}
                        </div>
                        <div class="progress-track" style="margin-top:8px;max-width:300px">
                            <div class="progress-fill" style="width:{pct}%"></div>
                        </div>
                        <div style="font-size:11px;color:#4b5563;margin-top:2px">{cumulative} / {available} min used</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with c_right:
        st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)
        remaining = available - cumulative
        used_pct  = min(int(cumulative / available * 100), 100)

        st.markdown(
            f'<div class="glass-card">'
            f'<p style="font-size:13px;color:#64748b;margin:0 0 4px">Time budget used</p>'
            f'<p style="font-size:32px;font-weight:800;color:#0ea5e9;margin:0">{used_pct}%</p>'
            f'<div class="progress-track" style="margin:10px 0">'
            f'<div class="progress-fill" style="width:{used_pct}%"></div></div>'
            f'<p style="font-size:13px;color:#64748b">{cumulative} min scheduled</p>'
            f'<p style="font-size:13px;color:#10b981">{remaining} min free</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Priority breakdown
        st.markdown('<p class="section-label" style="margin-top:16px">By Priority</p>', unsafe_allow_html=True)
        for pval in [5, 4, 3, 2, 1]:
            count = sum(1 for t in plan if t.priority == pval)
            if count:
                color = PRIORITY_COLORS[pval]
                bar_w = int(count / len(plan) * 100)
                st.markdown(
                    f'<div class="stat-row">'
                    f'<span class="stat-label" style="color:{color};font-size:11px;font-weight:600">'
                    f'{PRIORITY_LABELS[pval]}</span>'
                    f'<div class="stat-bar"><div class="stat-fill" style="width:{bar_w}%;background:{color}"></div></div>'
                    f'<span style="font-size:12px;color:#64748b;margin-left:6px">{count}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown('<p class="section-label">Scheduler Reasoning</p>', unsafe_allow_html=True)
    st.info(scheduler.explain_plan(plan))

    st.markdown("---")
    st.markdown('<p class="section-label">Find Next Available Slot</p>', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        slot_dur = st.number_input("Task duration to fit (min)", min_value=5, max_value=240, value=30, label_visibility="collapsed")
    with c2:
        find_btn = st.button("🔍 Find Slot", type="primary")

    if find_btn:
        result = scheduler.find_next_available_slot(slot_dur)
        if result["feasible"]:
            st.success(result["recommendation"])
            if result["earliest_slot"]:
                s, e = result["earliest_slot"]
                st.metric("Suggested Window", f"{s} – {e} min")
        else:
            st.warning(result["recommendation"])
        for alt in result.get("alternative_slots", []):
            st.info(f"• {alt['description']}")
        st.metric("Feasibility Score", f"{result['priority_score']}/100")
