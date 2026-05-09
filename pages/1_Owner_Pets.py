import streamlit as st
from pawpal_system import Owner, Pet
from utils import inject_css, init_state, sidebar_status, SPECIES_EMOJI

st.set_page_config(page_title="PawPal+ | Owner & Pets", page_icon="🐾", layout="wide", initial_sidebar_state="expanded")
inject_css()
init_state()
sidebar_status()

st.markdown('<p class="section-label">Profile</p>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Owner & Pets</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Set up your profile and register your pets</p>', unsafe_allow_html=True)

# ── Owner card ────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 👤 Owner Profile")

if st.session_state.owner:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;'
        f'padding:14px;background:rgba(14,165,233,0.08);border-radius:12px;'
        f'border:1px solid rgba(14,165,233,0.25)">'
        f'<div style="width:48px;height:48px;border-radius:50%;'
        f'background:linear-gradient(135deg,#0ea5e9,#38bdf8);display:flex;'
        f'align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white">'
        f'{st.session_state.owner.name[0].upper()}</div>'
        f'<div><p style="margin:0;font-weight:700;color:#075985;font-size:16px">'
        f'{st.session_state.owner.name}</p>'
        f'<p style="margin:0;color:#6b7280;font-size:13px">'
        f'{st.session_state.owner.available_minutes} min/day available</p></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

c1, c2 = st.columns(2)
with c1:
    owner_name = st.text_input(
        "Your name",
        value=st.session_state.owner.name if st.session_state.owner else "Jordan",
        placeholder="Enter your name"
    )
with c2:
    avail = st.number_input(
        "Daily time for pet care (minutes)",
        min_value=10, max_value=1440,
        value=st.session_state.owner.available_minutes if st.session_state.owner else 120,
    )

if st.button("✅ Save Owner Profile", type="primary"):
    st.session_state.owner = Owner(name=owner_name, available_minutes=avail)
    st.success(f"Profile saved — **{owner_name}** · {avail} min/day")
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.owner:
    st.warning("Save your profile to continue.")
    st.stop()

st.markdown("---")

# ── Add pet ───────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("#### 🐾 Add a Pet")
c1, c2, c3 = st.columns(3)
with c1:
    pet_name = st.text_input("Pet name", placeholder="e.g. Mochi")
with c2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"],
                           format_func=lambda x: f"{SPECIES_EMOJI.get(x,'🐾')} {x.capitalize()}")
with c3:
    age = st.number_input("Age (years)", min_value=0, max_value=50, value=3)

if st.button("➕ Add Pet", type="primary"):
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    elif pet_name in st.session_state.pets:
        st.warning(f"**{pet_name}** already exists.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.pets[pet_name] = new_pet
        st.session_state.owner.add_pet(new_pet)
        st.success(f"{SPECIES_EMOJI.get(species,'🐾')} **{pet_name}** added!")
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Pet grid ──────────────────────────────────────────────────────────────────
if st.session_state.pets:
    st.markdown("---")
    st.markdown('<p class="section-label">Your Pets</p>', unsafe_allow_html=True)
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
                    <p>{len(pet.tasks)} task(s) · {pet_pct}% done</p>
                    <div class="progress-track" style="margin-top:8px">
                        <div class="progress-fill" style="width:{pet_pct}%"></div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
