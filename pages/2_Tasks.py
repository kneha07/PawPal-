import re
import streamlit as st
import streamlit.components.v1 as components
from pawpal_system import Task, Scheduler
from utils import (inject_css, init_state, sidebar_status,
                   SPECIES_EMOJI, PRIORITY_LABELS, PRIORITY_COLORS,
                   render_task_list)

st.set_page_config(page_title="PawPal+ | Tasks", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
inject_css()
init_state()
sidebar_status()

st.markdown('<p class="section-label">Manage</p>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Tasks</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Add, view, filter, and complete pet care tasks</p>', unsafe_allow_html=True)

if not st.session_state.owner:
    st.warning("Set up your owner profile first in **Owner & Pets**.")
    st.stop()
if not st.session_state.pets:
    st.warning("Add at least one pet first in **Owner & Pets**.")
    st.stop()

# ── Voice-to-task parser ──────────────────────────────────────────────────────
def parse_voice_task(text):
    """Extract duration, time, and task name from a spoken phrase."""
    duration = 30
    sched    = ""
    m = re.search(r'(\d+)\s*min', text, re.I)
    if m: duration = int(m.group(1))
    m = re.search(r'\b(\d{1,2})[:\s]?(\d{2})?\s*(am|pm)\b', text, re.I)
    if m:
        h, mn, meridiem = m.group(1), m.group(2) or "00", m.group(3).lower()
        h = int(h)
        if meridiem == "pm" and h != 12: h += 12
        if meridiem == "am" and h == 12: h = 0
        sched = f"{h:02d}:{mn}"
    name = re.sub(r'(\d+\s*min(utes?)?)', '', text, flags=re.I)
    name = re.sub(r'\b\d{1,2}[:\s]?\d{0,2}\s*(am|pm)\b', '', name, flags=re.I)
    name = re.sub(r'\b(for|at|a|an|the|add|create)\b', '', name, flags=re.I)
    name = " ".join(name.split()).strip().capitalize() or text.strip().capitalize()
    return name, duration, sched

# ── Handle voice query param ──────────────────────────────────────────────────
raw_voice = st.query_params.get("task_voice", "")
if raw_voice and raw_voice != st.session_state.get("_last_task_voice", ""):
    name, dur, sched = parse_voice_task(raw_voice)
    st.session_state["voice_task_name_input"] = name
    st.session_state["voice_duration_input"]  = dur
    st.session_state["voice_time_input"]      = sched
    st.session_state["_last_task_voice"] = raw_voice
    st.query_params.clear()

# ── Add task ──────────────────────────────────────────────────────────────────
with st.expander("➕ Add New Task", expanded=True):

    # Mic button
    components.html("""
<style>
  *{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
  body{background:transparent;padding:4px 0}
  .row{display:flex;align-items:center;gap:10px}
  #btn{width:38px;height:38px;border-radius:50%;border:none;cursor:pointer;
    background:linear-gradient(135deg,#0369a1,#0ea5e9);
    box-shadow:0 3px 10px rgba(14,165,233,.4);font-size:16px;color:#fff;
    transition:all .2s ease;flex-shrink:0}
  #btn:hover{transform:scale(1.1)}
  #btn.on{background:linear-gradient(135deg,#dc2626,#f87171);
    animation:pulse 1s ease-in-out infinite}
  @keyframes pulse{0%,100%{box-shadow:0 3px 10px rgba(220,38,38,.5)}
    50%{box-shadow:0 3px 20px rgba(220,38,38,.9);transform:scale(1.06)}}
  #status{font-size:12px;color:#6b7280;font-weight:500}
  #status.on{color:#dc2626;font-weight:600}
  #status.ok{color:#0ea5e9;font-weight:600}
  #status.err{color:#f97316}
  .wave{display:none;gap:2px;align-items:flex-end;height:16px}
  .wave.show{display:flex}
  .wave b{display:block;width:3px;border-radius:2px;background:#dc2626}
  .wave b:nth-child(1){height:5px;animation:wv .8s 0s ease-in-out infinite}
  .wave b:nth-child(2){height:12px;animation:wv .8s .1s ease-in-out infinite}
  .wave b:nth-child(3){height:16px;animation:wv .8s .2s ease-in-out infinite}
  .wave b:nth-child(4){height:10px;animation:wv .8s .3s ease-in-out infinite}
  .wave b:nth-child(5){height:5px;animation:wv .8s .4s ease-in-out infinite}
  @keyframes wv{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}
</style>
<div class="row">
  <button id="btn">🎙️</button>
  <div class="wave" id="wave"><b></b><b></b><b></b><b></b><b></b></div>
  <span id="status">Say your task — e.g. "30 min walk at 8am"</span>
</div>
<script>
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  const btn=document.getElementById('btn'),wave=document.getElementById('wave'),stat=document.getElementById('status');
  if(!SR){btn.disabled=true;btn.style.opacity='.4';stat.textContent='⚠️ Use Chrome';stat.className='err';}
  else{
    const rec=new SR();rec.lang='en-US';rec.continuous=false;rec.interimResults=false;
    let on=false;
    function toggle(v){on=v;btn.classList.toggle('on',v);wave.classList.toggle('show',v);
      btn.textContent=v?'⏹️':'🎙️';
      if(v){stat.textContent='Listening…';stat.className='on';}}
    rec.onresult=(e)=>{
      const t=e.results[0][0].transcript.trim();
      stat.textContent='✅ '+t;stat.className='ok';
      const url=new URL(window.parent.location.href);
      url.searchParams.set('task_voice',t);
      window.parent.location.href=url.toString();
    };
    rec.onerror=(e)=>{stat.textContent=e.error==='not-allowed'?'🚫 Allow mic':'Try again';stat.className='err';toggle(false);};
    rec.onend=()=>toggle(false);
    btn.onclick=()=>on?rec.stop():(rec.start(),toggle(true));
  }
</script>
""", height=50)

    c1, c2, c3 = st.columns(3)
    with c1:
        sel_pet   = st.selectbox("Pet", list(st.session_state.pets.keys()),
                                 format_func=lambda x: f"{SPECIES_EMOJI.get(st.session_state.pets[x].species,'🐾')} {x}")
        task_name = st.text_input("Task name", placeholder="e.g. Morning walk",
                                  key="voice_task_name_input")
    with c2:
        duration  = st.number_input("Duration (min)", min_value=1, max_value=240,
                                    key="voice_duration_input")
        priority  = st.select_slider(
            "Priority", options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{PRIORITY_LABELS[x]} ({x})"
        )
    with c3:
        sched_time = st.text_input("Scheduled time (HH:MM)", placeholder="08:00",
                                   key="voice_time_input")
        recurring  = st.toggle("🔄 Recurring daily")

    # Priority preview
    color = PRIORITY_COLORS.get(priority, "#6b7280")
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:8px;margin-top:4px;'
        f'padding:6px 14px;background:{color}22;border:1px solid {color}44;'
        f'border-radius:99px;font-size:12px;font-weight:700;color:{color}">'
        f'Selected priority: {PRIORITY_LABELS[priority]}</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("➕ Add Task", type="primary"):
        if not task_name.strip():
            st.error("Task name cannot be empty.")
        else:
            t = Task(
                name=task_name, duration_minutes=duration,
                priority=priority, recurring=recurring,
                recurrence_pattern="daily" if recurring else None,
                scheduled_time=sched_time.strip() or None,
            )
            st.session_state.pets[sel_pet].add_task(t)
            st.success(f"✅ **{task_name}** added to {sel_pet}!")
            st.rerun()

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_all, tab_filter, tab_complete = st.tabs(["📋 All Tasks", "🔍 Filter & Search", "✅ Mark Complete"])

with tab_all:
    if not any(pet.tasks for pet in st.session_state.pets.values()):
        st.markdown('<p style="color:#4b5563;padding:20px 0">No tasks yet. Add one above!</p>', unsafe_allow_html=True)
    for pname, pet in st.session_state.pets.items():
        emoji    = SPECIES_EMOJI.get(pet.species, "🐾")
        done_cnt = sum(1 for t in pet.tasks if t.status == "completed")
        pct      = int(done_cnt / len(pet.tasks) * 100) if pet.tasks else 0
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px">'
            f'<span style="font-size:20px">{emoji}</span>'
            f'<span style="font-weight:700;font-size:15px;color:#075985">{pname}</span>'
            f'<span style="font-size:12px;color:#64748b">{len(pet.tasks)} tasks · {pct}% done</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        render_task_list(pet.tasks)

with tab_filter:
    all_tasks = st.session_state.owner.get_all_tasks()
    scheduler = Scheduler(st.session_state.owner)
    c1, c2, c3 = st.columns(3)
    with c1:
        status_f = st.selectbox("Status", ["all", "pending", "completed", "skipped"],
                                format_func=lambda x: "All statuses" if x == "all" else x.capitalize())
    with c2:
        pet_f = st.selectbox("Pet", ["all"] + list(st.session_state.pets.keys()),
                              format_func=lambda x: "All pets" if x == "all" else
                              f"{SPECIES_EMOJI.get(st.session_state.pets[x].species,'🐾')} {x}" if x != "all" else x)
    with c3:
        priority_f = st.selectbox("Priority", ["all", 1, 2, 3, 4, 5],
                                   format_func=lambda x: "All priorities" if x == "all" else PRIORITY_LABELS[x])

    filtered = all_tasks
    if status_f   != "all": filtered = scheduler.filter_tasks_by_status(filtered, status_f)
    if pet_f      != "all": filtered = scheduler.filter_tasks_by_pet(filtered, pet_f)
    if priority_f != "all": filtered = [t for t in filtered if t.priority == priority_f]

    st.markdown(
        f'<p style="font-size:13px;color:#64748b;margin-bottom:12px">'
        f'{len(filtered)} task(s) found</p>',
        unsafe_allow_html=True,
    )
    render_task_list(filtered)

with tab_complete:
    all_tasks = st.session_state.owner.get_all_tasks()
    pending   = [t for t in all_tasks if t.status == "pending"]

    if not pending:
        st.success("🎉 All done for today!")
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            opts = {f"{t.name} — {PRIORITY_LABELS[t.priority]}": t for t in pending}
            sel  = st.selectbox("Select task to complete", list(opts.keys()))
        with c2:
            st.write("")
            st.write("")
            if st.button("✅ Mark Complete", type="primary", use_container_width=True):
                task = opts[sel]
                nxt  = task.mark_complete()
                st.success(f"✅ **{task.name}** completed!")
                if nxt:
                    for pet in st.session_state.owner.pets:
                        if task in pet.tasks:
                            pet.add_task(nxt)
                            break
                    st.info("🔄 Next recurrence scheduled.")
                st.rerun()

    st.markdown("---")
    all_t = st.session_state.owner.get_all_tasks()
    done  = sum(1 for t in all_t if t.status == "completed")
    pct   = int(done / len(all_t) * 100) if all_t else 0

    st.markdown('<p class="section-label">Today\'s Progress</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="progress-track" style="height:12px;margin-bottom:8px">'
        f'<div class="progress-fill" style="width:{pct}%"></div></div>'
        f'<p style="font-size:13px;color:#64748b">{done} of {len(all_t)} tasks complete · {pct}%</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Pending",   len(pending) if pending else 0)
    c2.metric("Completed", done)
    c3.metric("Progress",  f"{pct}%")
