import streamlit as st
import google.generativeai as genai
import json
import html as html_lib

# ---------------------------------------------------------------------------
# 1. Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Scope Creep Analyzer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.6-flash"

st.session_state.setdefault("result", None)
st.session_state.setdefault("error", None)

# ---------------------------------------------------------------------------
# 2. Design System — Ultra-Level Cinematic Brutalist / Dark Swiss
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@700;900&family=Inter:wght@300;400;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
  --bg-deep: #050505;
  --bg-surface: #0E0E0E;
  --ink: #F4F4F0;
  --ink-dim: #888888;
  --rule: #222222;
  --rule-hover: #444444;
  --red: #FF2A2A;
  --green: #00E65B;
  --amber: #FFB300;
  --accent: #FFFFFF;
}

/* Base override for a true dark mode experience */
html, body, [class*="css"], .stApp { 
    font-family: 'Inter', sans-serif; 
    background-color: var(--bg-deep) !important; 
    color: var(--ink) !important; 
}

/* Sidebar එකේ ඊතලය පෙන්වීමට Header එක Transparent කිරීම */
#MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

.block-container { 
    max-width: 1040px; 
    padding-top: 4rem; 
    padding-bottom: 6rem; 
}

/* ---------- Typography & Layout ---------- */
::selection { background: var(--accent); color: var(--bg-deep); }

/* ---------- Masthead ---------- */
.sca-masthead { display: flex; align-items: flex-start; gap: 24px; animation: fadeDown 0.8s ease-out; }
.sca-mark { 
    background: var(--ink); color: var(--bg-deep); font-family: 'Archivo'; font-weight: 900;
    font-size: 14px; letter-spacing: 0.1em; padding: 10px 14px; margin-top: 6px; 
}
.sca-ref { 
    font-family: 'IBM Plex Mono'; font-size: 10px; letter-spacing: 0.15em; color: var(--ink-dim);
    text-transform: uppercase; margin-bottom: 8px; 
}
.sca-masthead h1 { 
    font-family: 'Archivo'; font-weight: 900; font-size: clamp(32px, 4vw, 56px);
    letter-spacing: -0.02em; text-transform: uppercase; line-height: 1; margin: 0; color: var(--ink);
}
.sca-sub { 
    font-family: 'IBM Plex Mono'; font-size: 12px; color: var(--ink-dim); letter-spacing: 0.04em;
    margin-top: 12px; max-width: 600px; line-height: 1.4;
}
.sca-rule-thick { height: 4px; background: var(--ink); margin-top: 32px; }
.sca-rule-thin { height: 1px; background: var(--rule); margin: 4px 0 48px 0; }

/* ---------- Numbered section headers ---------- */
.sca-section { 
    display: flex; align-items: baseline; gap: 16px; margin: 56px 0 24px 0;
    border-bottom: 1px solid var(--rule); padding-bottom: 12px; 
}
.sca-section .num { font-family: 'IBM Plex Mono'; font-weight: 600; font-size: 14px; color: var(--red); }
.sca-section .title { 
    font-family: 'Archivo'; font-weight: 700; font-size: 15px; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--ink);
}

/* ---------- Baseline stat strip ---------- */
.sca-stats { 
    display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid var(--rule); 
    background: var(--bg-surface);
}
.sca-stat { 
    padding: 24px 28px; border-right: 1px solid var(--rule); transition: all 0.3s ease;
}
.sca-stat:hover { background: #151515; border-color: var(--rule-hover); }
.sca-stat:last-child { border-right: none; }
.sca-stat .label { 
    display: block; font-family: 'IBM Plex Mono'; font-size: 10px; letter-spacing: 0.1em;
    color: var(--ink-dim); text-transform: uppercase; margin-bottom: 12px; 
}
.sca-stat .value { font-family: 'Archivo'; font-weight: 900; font-size: 32px; letter-spacing: -0.02em; }
.sca-stat .value.neg { color: var(--red); }

/* ---------- Sidebar Re-styling ---------- */
section[data-testid="stSidebar"] { 
    background-color: var(--bg-surface) !important; border-right: 1px solid var(--rule); 
}
section[data-testid="stSidebar"] .sca-side-title { 
    font-family: 'Archivo'; font-weight: 900; font-size: 18px; color: var(--ink);
    text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid var(--ink);
    padding-bottom: 16px; margin-bottom: 32px; 
}

/* ---------- Deep Streamlit UI Overrides ---------- */
/* Inputs */
div[data-baseweb="textarea"] > div, 
div[data-baseweb="input"] > div {
    background-color: var(--bg-deep) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 0 !important;
    transition: border-color 0.3s ease;
}
div[data-baseweb="textarea"]:focus-within > div, 
div[data-baseweb="input"]:focus-within > div {
    border-color: var(--ink) !important;
}
textarea, input {
    font-family: 'IBM Plex Mono' !important; 
    font-size: 13px !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}

/* Buttons */
div[data-testid="stButton"] button {
    background: var(--ink) !important; 
    color: var(--bg-deep) !important; 
    border: none !important;
    border-radius: 0 !important; 
    font-family: 'IBM Plex Mono' !important; 
    font-weight: 600 !important; 
    letter-spacing: 0.1em !important; 
    text-transform: uppercase !important;
    font-size: 13px !important; 
    padding: 24px 32px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover { 
    background: var(--red) !important; 
    color: #FFF !important; 
    transform: translateY(-2px);
}

/* ---------- Verdict Components ---------- */
/* Entry Animations */
@keyframes slideUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes fadeDown {
    0% { opacity: 0; transform: translateY(-15px); }
    100% { opacity: 1; transform: translateY(0); }
}

.sca-reveal { animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

.sca-stamp { 
    padding: 28px 32px; font-family: 'Archivo'; font-weight: 900; font-size: 28px;
    letter-spacing: 0.05em; text-transform: uppercase; border: 1px solid transparent;
}
.sca-stamp.out { background: rgba(255,42,42,0.05); color: var(--red); border-color: var(--red); }
.sca-stamp.in { background: rgba(0,230,91,0.05); color: var(--green); border-color: var(--green); }
.sca-stamp.review { background: rgba(255,179,0,0.05); color: var(--amber); border-color: var(--amber); }

.sca-docket { border: 1px solid var(--rule); border-top: none; background: var(--bg-surface); }
.sca-row { display: grid; grid-template-columns: 220px 1fr; border-bottom: 1px solid var(--rule); }
.sca-row:last-child { border-bottom: none; }
.sca-row .k { 
    font-family: 'IBM Plex Mono'; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--ink-dim); padding: 24px; border-right: 1px solid var(--rule); 
}
.sca-row .v { padding: 24px; font-size: 15px; line-height: 1.6; color: #D0D0D0; font-family: 'Inter'; font-weight: 300; }
.sca-row .v.mono { font-family: 'IBM Plex Mono'; color: var(--ink); }
.sca-row .v.cost { font-family: 'IBM Plex Mono'; font-weight: 600; font-size: 22px; color: var(--ink); }
.sca-row .v.cost.flag { color: var(--red); }

/* ---------- Empty state ---------- */
.sca-empty { 
    border: 1px dashed var(--rule); padding: 48px 32px; font-family: 'IBM Plex Mono';
    font-size: 12px; color: var(--ink-dim); text-transform: uppercase; letter-spacing: 0.1em; 
    text-align: center; background: var(--bg-surface);
}

/* ---------- Expander ---------- */
div[data-testid="stExpander"] { border-radius: 0; border: 1px solid var(--rule); background: var(--bg-deep); }
div[data-testid="stExpander"] summary { font-family: 'IBM Plex Mono'; color: var(--ink-dim); }

@media (max-width: 768px){
  .sca-stats { grid-template-columns: repeat(2, 1fr); }
  .sca-stats .sca-stat:nth-child(2) { border-right: none; }
  .sca-row { grid-template-columns: 1fr; }
  .sca-row .k { border-right: none; border-bottom: 1px solid var(--rule); padding: 16px; }
  .sca-row .v { padding: 16px; }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 3. Masthead
# ---------------------------------------------------------------------------
st.markdown("""
<div class="sca-masthead">
  <div class="sca-mark">SCA</div>
  <div>
    <div class="sca-ref">Terminal Module 04 &middot; Protocol Audit</div>
    <h1>Scope Creep Analyzer</h1>
    <div class="sca-sub">NLP Classification Engine for fixed project baselines.</div>
  </div>
</div>
<div class="sca-rule-thick"></div>
<div class="sca-rule-thin"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 4. Sidebar Configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### PROJECT BASELINE")
    max_revs = st.number_input("Max Revisions Allowed", min_value=1, value=3)
    used_revs = st.number_input("Revisions Used So Far", min_value=0, value=2)
    extra_cost = st.number_input("Cost per Extra Revision ($)", min_value=0, value=50)
    st.divider()

# ---------------------------------------------------------------------------
# 5. Baseline Stat Strip
# ---------------------------------------------------------------------------
remaining = max_revs - used_revs
st.markdown(f"""
<div class="sca-stats">
  <div class="sca-stat"><span class="label">Max Revisions</span><span class="value">{max_revs}</span></div>
  <div class="sca-stat"><span class="label">Used</span><span class="value">{used_revs}</span></div>
  <div class="sca-stat"><span class="label">Remaining</span><span class="value {'neg' if remaining < 0 else ''}">{remaining}</span></div>
  <div class="sca-stat"><span class="label">Cost / Extra Rev</span><span class="value">${extra_cost}</span></div>
</div>
""", unsafe_allow_html=True)

def section_header(number: str, title: str) -> None:
    st.markdown(
        f'<div class="sca-section"><span class="num">{number}</span>'
        f'<span class="title">{title}</span></div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 6. Input Area
# ---------------------------------------------------------------------------
section_header("01", "Client Transmission")
client_message = st.text_area(
    "Client Message",
    height=180,
    placeholder="Paste the unstructured client request here...",
    label_visibility="collapsed",
)

st.write("") # Spacer
_, btn_col = st.columns([4, 1.2])
with btn_col:
    run = st.button("Execute Audit", type="primary", use_container_width=True)

# System Prompt v4.0 (Backend logic untouched)
SYSTEM_PROMPT = """
[System Role]
You are an impartial, highly analytical Project Scope Analyzer. Your sole function is to evaluate unstructured client messages against rigid project baselines. Do not make assumptions, and do not attempt to be helpful or polite.

[Definitions & Constraints]
- "in_scope": A request unit that does not add a net-new feature, page, or medium, and does not cause cumulative revisions to exceed `max_revisions`.
- "out_of_scope": A request unit introducing new deliverables (e.g., new pages, mediums, technical complexities not previously discussed), OR any unit whose inclusion causes `revisions_used` + (count of chargeable units) > `max_revisions`.
- "review_needed": A request unit containing subjective terminology (e.g., "modern", "vibe"), ambiguous pronouns, or emotional manipulation/urgency, where computational limits cannot be strictly applied, AND which does not independently qualify as out_of_scope.
- A "request unit" is one discrete, independently-actionable deliverable, feature, or action ask. Units are defined by distinct intent, not by sentence grammar alone.

[Execution Logic]
1. DECOMPOSE the `new_client_message` into N request units based on distinct deliverables, actions, or asks — not grammar alone. Subordinate, dependent, or minimizing constructions (e.g., "while," "since," "as long as," "just," "quick," "since you're already in there") do NOT exempt an embedded ask from decomposition. If a subordinate or dependent clause introduces a deliverable, feature, or complexity distinct from the primary clause, it MUST be split out as its own unit regardless of conjunction type or sentence structure.
2. PER-UNIT CLASSIFICATION: Evaluate each unit independently against the Definitions.
   a. IF a unit introduces items, complexities, or features not explicitly covered in `project_baseline` → unit = "out_of_scope".
   b. IF a unit is a revision and `revisions_used` + (running count of chargeable units, including this one) > `max_revisions` → unit = "out_of_scope"; record which unit(s) exceed the balance.
   c. IF a unit is ambiguous, subjective, or contains urgency/emotional pressure AND does not already satisfy 2a or 2b → unit = "review_needed".
   d. Otherwise → unit = "in_scope".
   Within a single unit, if multiple conditions apply simultaneously: out_of_scope > review_needed > in_scope.
3. AGGREGATE all unit-level classifications into one message-level `status` using the severity hierarchy: out_of_scope > review_needed > in_scope. The message-level `status` equals the highest-severity classification present across all units.
   - `exact_client_quote` = the unit that produced the highest-severity classification (if tied, the first such unit in message order).
   - IF multiple units are "out_of_scope", `reason` must briefly enumerate each contributing unit; do not report only one.
4. IF message-level `status` = "out_of_scope", calculate `extra_cost_usd` as the SUM of `cost_per_extra_revision` across every unit classified "out_of_scope" — not a single instance.

[Strict Data Integrity Rules]
- NO PARAPHRASING: You must extract the exact words from the client message.
- JSON ESCAPING MANDATE: "Verbatim" governs word choice only, never character encoding. Escape backslashes FIRST, before any other character, to prevent double-escaping and to guarantee no unescaped backslash is left immediately adjacent to a delimiter. After that, escape all characters required under RFC 8259 Section 7 — this includes but is not limited to double quotes and ALL control characters in the range U+0000–U+001F (newlines, carriage returns, tabs, form feeds, vertical tabs, and any other control byte), not solely the examples named here.
- LENGTH BOUND: `exact_client_quote` must isolate only the single unit identified in Execution Logic Step 3 (max ~200 chars). Do not quote the entire message.
- REASONING LIMITATION: The `reason` field must ONLY isolate the problematic condition(s) per Step 3. Do not explain vocabulary or assume intent.
- STRICT FORMAT: You must output ONLY a valid JSON object. No conversational text before or after the JSON.

[Output JSON Schema]
{
  "status": "in_scope" | "out_of_scope" | "review_needed",
  "exact_client_quote": "string",
  "reason": "string",
  "extra_cost_usd": 0,
  "suggested_action": "string"
}
"""

# ---------------------------------------------------------------------------
# 7. Processing Logic
# ---------------------------------------------------------------------------
if run:
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error("SYSTEM HALT: API Key not configured in Cloud Secrets.")
    elif not client_message:
        st.warning("SYSTEM HALT: Client transmission empty.")
    else:
        with st.spinner("Compiling logic..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(MODEL_NAME)

                prompt = f"""
                System Instructions: {SYSTEM_PROMPT}

                Project Baseline:
                - max_revisions: {max_revs}
                - revisions_used: {used_revs}
                - cost_per_extra_revision: {extra_cost}

                new_client_message: "{client_message}"
                """

                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    ),
                )

                st.session_state["result"] = json.loads(response.text)
                st.session_state["error"] = None
            except Exception as e:
                st.session_state["error"] = str(e)

# ---------------------------------------------------------------------------
# 8. Verdict Engine UI
# ---------------------------------------------------------------------------
section_header("02", "Audit Verdict")

if st.session_state["error"]:
    st.error(f"FATAL ERROR: {st.session_state['error']}")

elif st.session_state["result"]:
    result = st.session_state["result"]
    status = result.get("status", "review_needed")
    status_class = {"in_scope": "in", "out_of_scope": "out", "review_needed": "review"}.get(status, "review")
    cost = result.get("extra_cost_usd", 0) or 0
    quote = html_lib.escape(str(result.get("exact_client_quote", "")))
    reason = html_lib.escape(str(result.get("reason", "")))
    action = html_lib.escape(str(result.get("suggested_action", "Review required.")))

    # Wrapped in animation class 'sca-reveal'
    st.markdown(f'''
    <div class="sca-reveal">
        <div class="sca-stamp {status_class}">STATUS // {status.replace("_", " ")}</div>
        <div class="sca-docket">
          <div class="sca-row"><div class="k">Exact Extract</div><div class="v mono">&ldquo;{quote}&rdquo;</div></div>
          <div class="sca-row"><div class="k">Logic Trigger</div><div class="v">{reason}</div></div>
          <div class="sca-row"><div class="k">Cost Impact</div><div class="v cost {'flag' if cost > 0 else ''}">${cost:,.2f}{'' if cost > 0 else ' — No overage detected'}</div></div>
          <div class="sca-row"><div class="k">System Action</div><div class="v">{action}</div></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.write("")
    with st.expander("ACCESS RAW JSON PAYLOAD"):
        st.json(result)

else:
    st.markdown(
        '<div class="sca-empty">Awaiting data transmission. Execute audit to proceed.</div>',
        unsafe_allow_html=True,
    )
