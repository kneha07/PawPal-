import logging
import streamlit as st
from google.genai import types
from utils import inject_css, init_state, sidebar_status, gemini_client
from rag_engine import RAGEngine
from agent_tools import TOOL_DECLARATIONS, execute_tool

import streamlit.components.v1 as components

st.set_page_config(page_title="PawPal+ | AI Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
inject_css()
init_state()
sidebar_status()

logger = logging.getLogger(__name__)

st.markdown('<p class="section-label">AI-Powered</p>', unsafe_allow_html=True)
st.markdown('<p class="page-title">PawPal AI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Ask anything about your pets — or let the AI manage your schedule</p>', unsafe_allow_html=True)

# ── RAG ───────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_rag():
    return RAGEngine("pet_care_kb.txt")
rag = get_rag()

# ── Tool config ───────────────────────────────────────────────────────────────
gemini_tools = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name=t["name"], description=t["description"],
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                k: types.Schema(
                    type=types.Type.STRING  if v["type"] == "string"  else
                         types.Type.INTEGER if v["type"] == "integer" else
                         types.Type.BOOLEAN,
                    description=v.get("description", "")
                ) for k, v in t["parameters"].get("properties", {}).items()
            },
            required=t["parameters"].get("required", [])
        )
    ) for t in TOOL_DECLARATIONS
])


def build_system_prompt(rag_context: str = "") -> str:
    prompt = (
        "You are PawPal AI, a friendly and knowledgeable pet care assistant. "
        "You have tools to list pets, list tasks, add tasks, generate schedules, and check conflicts. "
        "Use tools proactively when the user's request involves scheduling or task management. "
        "Be warm, concise, and practical.\n\n"
    )
    if st.session_state.owner:
        prompt += f"Owner: {st.session_state.owner.name}, {st.session_state.owner.available_minutes} min/day.\n"
        if st.session_state.pets:
            prompt += "Pets:\n"
            for pet in st.session_state.pets.values():
                tasks = ", ".join(t.name for t in pet.tasks) or "no tasks"
                prompt += f"  - {pet.name} ({pet.species}, {pet.age}yr): {tasks}\n"
    if rag_context:
        prompt += f"\n--- Pet Care Knowledge ---\n{rag_context}\n---\n"
    return prompt


# ── Capabilities banner ───────────────────────────────────────────────────────
st.markdown(
    '<div class="card" style="margin-bottom:20px">'
    '<p style="font-size:13px;font-weight:600;color:#0ea5e9;margin:0 0 10px">What I can do for you</p>'
    '<div style="display:flex;flex-wrap:wrap;gap:8px">'
    '<span style="background:#f0f9ff;border:1px solid #bae6fd;padding:5px 12px;border-radius:99px;font-size:12px;color:#0284c7">📋 Add tasks</span>'
    '<span style="background:#f0fdf4;border:1px solid #bbf7d0;padding:5px 12px;border-radius:99px;font-size:12px;color:#15803d">📅 Generate schedules</span>'
    '<span style="background:#fff7ed;border:1px solid #fed7aa;padding:5px 12px;border-radius:99px;font-size:12px;color:#c2410c">⚠️ Detect conflicts</span>'
    '<span style="background:#f0f9ff;border:1px solid #7dd3fc;padding:5px 12px;border-radius:99px;font-size:12px;color:#0369a1">🔍 Answer pet care questions</span>'
    '<span style="background:#fdf4ff;border:1px solid #e9d5ff;padding:5px 12px;border-radius:99px;font-size:12px;color:#7e22ce">📚 Knowledge base (RAG)</span>'
    '<span style="background:#f0f9ff;border:1px solid #bae6fd;padding:5px 12px;border-radius:99px;font-size:12px;color:#0284c7">🎙️ Voice input</span>'
    '</div></div>',
    unsafe_allow_html=True,
)

# ── Quick prompt chips ────────────────────────────────────────────────────────
st.markdown('<p style="font-size:12px;font-weight:600;color:#4b5563;margin-bottom:8px">Quick prompts</p>', unsafe_allow_html=True)
chips = [
    ("📋 List pets",        "List my pets and tasks"),
    ("➕ Add task",         "Add a 30 min walk for Mochi at 8am"),
    ("📅 Schedule",         "Generate my schedule"),
    ("⚠️ Conflicts",       "Check for conflicts"),
    ("🐕 Groom tips",      "How often should I groom my dog?"),
    ("💊 Give pill",        "How do I give my cat a pill?"),
]

chip_cols = st.columns(len(chips))
for col, (label, prompt) in zip(chip_cols, chips):
    with col:
        st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
        if st.button(label, use_container_width=True, key=f"chip_{prompt[:10]}"):
            st.session_state._chip_input = prompt
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state.chat_messages:
    st.markdown(
        '<div style="text-align:center;padding:40px 0">'
        '<p style="font-size:40px">🐾</p>'
        '<p style="color:#9ca3af;font-size:14px">No messages yet. Ask me anything about your pets!</p>'
        '</div>',
        unsafe_allow_html=True,
    )

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Voice input ───────────────────────────────────────────────────────────────
voice_input = None
raw_voice = st.query_params.get("voice", "")
if raw_voice and raw_voice != st.session_state.get("_last_voice", ""):
    voice_input = raw_voice
    st.session_state["_last_voice"] = raw_voice
    st.query_params.clear()

components.html("""
<style>
  *{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
  body{background:transparent;padding:6px 2px}
  .row{display:flex;align-items:center;gap:12px}
  #btn{width:44px;height:44px;border-radius:50%;border:none;cursor:pointer;
    background:linear-gradient(135deg,#0369a1,#0ea5e9);
    box-shadow:0 3px 12px rgba(14,165,233,.4);font-size:18px;color:#fff;
    transition:all .2s ease;flex-shrink:0}
  #btn:hover{transform:scale(1.08)}
  #btn.on{background:linear-gradient(135deg,#dc2626,#f87171);
    animation:pulse 1s ease-in-out infinite}
  @keyframes pulse{0%,100%{box-shadow:0 3px 12px rgba(220,38,38,.5)}
    50%{box-shadow:0 3px 22px rgba(220,38,38,.9);transform:scale(1.06)}}
  #status{font-size:13px;color:#6b7280;font-weight:500}
  #status.on{color:#dc2626;font-weight:600}
  #status.ok{color:#0ea5e9;font-weight:600}
  #status.err{color:#f97316}
  .wave{display:none;gap:3px;align-items:flex-end;height:18px}
  .wave.show{display:flex}
  .wave b{display:block;width:3px;border-radius:2px;background:#dc2626}
  .wave b:nth-child(1){height:6px;animation:wv .8s 0s ease-in-out infinite}
  .wave b:nth-child(2){height:14px;animation:wv .8s .1s ease-in-out infinite}
  .wave b:nth-child(3){height:18px;animation:wv .8s .2s ease-in-out infinite}
  .wave b:nth-child(4){height:12px;animation:wv .8s .3s ease-in-out infinite}
  .wave b:nth-child(5){height:6px;animation:wv .8s .4s ease-in-out infinite}
  @keyframes wv{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}
</style>
<div class="row">
  <button id="btn">🎙️</button>
  <div class="wave" id="wave"><b></b><b></b><b></b><b></b><b></b></div>
  <span id="status">Click mic and speak your question</span>
</div>
<script>
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const btn = document.getElementById('btn');
  const wave = document.getElementById('wave');
  const stat = document.getElementById('status');
  if (!SR) {
    btn.disabled=true; btn.style.opacity='.4';
    stat.textContent='⚠️ Use Chrome for voice'; stat.className='err';
  } else {
    const rec = new SR();
    rec.lang='en-US'; rec.continuous=false; rec.interimResults=false;
    let on=false;
    function toggle(v){
      on=v; btn.classList.toggle('on',v); wave.classList.toggle('show',v);
      btn.textContent=v?'⏹️':'🎙️';
      if(v){stat.textContent='Listening…';stat.className='on';}
    }
    rec.onresult=(e)=>{
      const t=e.results[0][0].transcript.trim();
      stat.textContent='✅ '+t; stat.className='ok';
      const url=new URL(window.parent.location.href);
      url.searchParams.set('voice', t);
      window.parent.location.href=url.toString();
    };
    rec.onerror=(e)=>{
      stat.textContent=e.error==='not-allowed'?'🚫 Allow mic in browser':'No speech — try again';
      stat.className='err'; toggle(false);
    };
    rec.onend=()=>toggle(false);
    btn.onclick=()=>on?rec.stop():(rec.start(),toggle(true));
  }
</script>
""", height=58)

# ── Input ─────────────────────────────────────────────────────────────────────
chip_input = st.session_state.pop("_chip_input", None)
user_input = st.chat_input("Ask about your pets, or say 'add a walk for Mochi at 8am'...") or chip_input or voice_input

if user_input:
    logger.info(f"User: {user_input}")
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            rag_context = rag.retrieve(user_input)
            history = [
                types.Content(
                    role=m["role"] if m["role"] == "user" else "model",
                    parts=[types.Part(text=m["content"])]
                )
                for m in st.session_state.chat_messages[:-1]
            ]
            history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

            reply_placeholder = st.empty()
            tool_status       = st.empty()
            reply = ""

            # Try models in order — fallback if quota exceeded
            MODELS = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-2.5-flash"]
            def call_gemini(history):
                last_err = None
                for model in MODELS:
                    try:
                        return gemini_client.models.generate_content(
                            model=model, contents=history,
                            config=types.GenerateContentConfig(
                                system_instruction=build_system_prompt(rag_context),
                                tools=[gemini_tools],
                            )
                        )
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            last_err = e
                            continue
                        raise
                raise last_err

            for _ in range(5):
                response   = call_gemini(history)
                candidate  = response.candidates[0]
                tool_calls = [p for p in candidate.content.parts if p.function_call]

                if tool_calls:
                    history.append(candidate.content)
                    results = []
                    for tc in tool_calls:
                        fn = tc.function_call
                        tool_status.markdown(
                            f'<div style="display:inline-flex;align-items:center;gap:8px;'
                            f'padding:8px 16px;background:#f0f9ff;'
                            f'border:1px solid #bae6fd;border-radius:10px;'
                            f'font-size:13px;color:#0284c7">🔧 Running <code>{fn.name}</code>…</div>',
                            unsafe_allow_html=True,
                        )
                        result = execute_tool(fn.name, dict(fn.args), st.session_state.owner, st.session_state.pets)
                        results.append(types.Part(
                            function_response=types.FunctionResponse(
                                name=fn.name, response={"result": result}
                            )
                        ))
                    history.append(types.Content(role="user", parts=results))
                else:
                    tool_status.empty()
                    reply = "".join(p.text for p in candidate.content.parts if p.text)
                    reply_placeholder.markdown(reply)
                    break
            else:
                reply = "Done! Check the app for updates."
                reply_placeholder.markdown(reply)

            logger.info(f"Assistant: {reply[:120]}")
        except Exception as e:
            logger.error(f"Chat error: {e}")
            reply = f"Sorry, I ran into an error: {e}"
            st.markdown(reply)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── Clear chat ────────────────────────────────────────────────────────────────
if st.session_state.chat_messages:
    if st.button("🗑️ Clear chat", key="clear_chat"):
        st.session_state.chat_messages = []
        st.rerun()
