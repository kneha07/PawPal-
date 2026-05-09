import streamlit as st
from utils import inject_css, init_state, sidebar_status, SPECIES_EMOJI, render_task_list

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide", initial_sidebar_state="expanded")
inject_css()
init_state()
sidebar_status()

# ── Hero ──────────────────────────────────────────────────────────────────────
if st.session_state.owner:
    name = st.session_state.owner.name
    st.markdown(
        f'<div class="hero">'
        f'<h1>Good day, {name}! 🐾</h1>'
        f'<p>Here\'s an overview of your pet care for today.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="hero">'
        '<h1>Welcome to PawPal+ 🐾</h1>'
        '<p>Your AI-powered pet care scheduling assistant. Set up your profile to get started.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.info("👈 Set up your owner profile in **Owner & Pets** to begin.")
    st.stop()

owner     = st.session_state.owner
all_tasks = owner.get_all_tasks()
pending   = [t for t in all_tasks if t.status == "pending"]
completed = [t for t in all_tasks if t.status == "completed"]
pct       = int(len(completed) / len(all_tasks) * 100) if all_tasks else 0

# ── Metrics ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("🐾 Pets",        len(st.session_state.pets))
c2.metric("📋 Total Tasks", len(all_tasks))
c3.metric("✅ Done Today",   len(completed))
c4.metric("📈 Progress",     f"{pct}%")

st.markdown("---")

# ── Pet cards ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Your Pets</p>', unsafe_allow_html=True)

if not st.session_state.pets:
    st.caption("No pets yet — add them in **Owner & Pets**.")
else:
    cols = st.columns(min(len(st.session_state.pets), 4))
    for i, (_, pet) in enumerate(st.session_state.pets.items()):
        emoji    = SPECIES_EMOJI.get(pet.species, "🐾")
        pet_done = sum(1 for t in pet.tasks if t.status == "completed")
        pet_pct  = int(pet_done / len(pet.tasks) * 100) if pet.tasks else 0
        with cols[i % 4]:
            st.markdown(
                f"""<div class="pet-card">
                    <span class="pet-emoji">{emoji}</span>
                    <h3>{pet.name}</h3>
                    <p>{pet.species.capitalize()} · {pet.age} yrs</p>
                    <p style="margin-top:10px">
                        <span style="font-size:18px;font-weight:700;color:#075985">{pet_pct}%</span>
                        <span style="color:#0284c7;font-size:13px"> done</span>
                    </p>
                    <div class="progress-track" style="margin-top:6px">
                        <div class="progress-fill" style="width:{pet_pct}%"></div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

st.markdown("---")

# ── Pending tasks ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Pending Tasks</p>', unsafe_allow_html=True)
if pending:
    render_task_list(pending[:6])
    if len(pending) > 6:
        st.caption(f"…and {len(pending)-6} more in **Tasks**.")
else:
    st.success("🎉 All tasks completed for today!")

# ── Overall progress bar ──────────────────────────────────────────────────────
if all_tasks:
    st.markdown("---")
    st.markdown('<p class="section-label">Today\'s Overall Progress</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="progress-track" style="height:12px">'
        f'<div class="progress-fill" style="width:{pct}%"></div></div>'
        f'<p style="font-size:13px;color:#64748b;margin-top:6px">'
        f'{len(completed)} of {len(all_tasks)} tasks complete</p>',
        unsafe_allow_html=True,
    )
