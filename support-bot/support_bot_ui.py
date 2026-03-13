import streamlit as st
import time
from datetime import datetime
import random

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Limi AI — Support Bot",
    layout="wide",
    page_icon="🔧",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Space+Grotesk:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark industrial theme */
.stApp {
    background: #0a0c10;
    color: #e0e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e2d3d;
}

/* Headers */
h1, h2, h3 { font-family: 'JetBrains Mono', monospace !important; }

/* Cards */
.fault-card {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}

.normal-card {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}

.rag-output {
    background: #0d1f0d;
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
    color: #86efac;
    white-space: pre-wrap;
}

.email-preview {
    background: #1a1a2e;
    border: 1px solid #3b4f8c;
    border-radius: 8px;
    padding: 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.7;
    color: #c7d4f0;
}

.email-header {
    background: #16213e;
    border-bottom: 1px solid #3b4f8c;
    padding: 10px 24px;
    border-radius: 8px 8px 0 0;
    font-size: 11px;
    color: #8899bb;
    font-family: 'JetBrains Mono', monospace;
}

.step-badge {
    display: inline-block;
    background: #1d4ed8;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    text-align: center;
    line-height: 24px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 8px;
    font-family: 'JetBrains Mono', monospace;
}

.metric-box {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #60a5fa;
}

.metric-label {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.risk-high { color: #ef4444 !important; }
.risk-medium { color: #f59e0b !important; }
.risk-low { color: #22c55e !important; }

.log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #6b7280;
    padding: 2px 0;
}

.log-line.active { color: #22c55e; }
.log-line.error { color: #ef4444; }
.log-line.warn { color: #f59e0b; }

.pipeline-step {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 6px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.tag-critical { background: #450a0a; color: #ef4444; border: 1px solid #ef4444; }
.tag-warning { background: #451a03; color: #f59e0b; border: 1px solid #f59e0b; }
.tag-normal { background: #052e16; color: #22c55e; border: 1px solid #22c55e; }
.tag-faiss { background: #0c1a4a; color: #60a5fa; border: 1px solid #3b82f6; }
.tag-llama { background: #2d1f4a; color: #a78bfa; border: 1px solid #8b5cf6; }

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white;
    border: none;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 13px;
    padding: 10px 24px;
    cursor: pointer;
    transition: all 0.2s;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

div[data-testid="stSlider"] label { color: #8899bb; font-size: 12px; }
div[data-testid="stSelectbox"] label { color: #8899bb; font-size: 12px; }
div[data-testid="stNumberInput"] label { color: #8899bb; font-size: 12px; }

.stProgress > div > div { background: #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# ─── MOCK DATA ─────────────────────────────────────────────────────────────────
MANUAL_EXCERPTS = {
    "OVERHEAT_001": """=== FAULT CODE: OVERHEAT_001 ===
Symptom: Module internal temperature exceeds 65°C

Repair Steps:
  1. Check ambient room temperature — should be below 35°C
  2. Inspect cooling vents for dust blockage using compressed air
  3. Verify airflow clearance — minimum 10cm on all sides
  4. Check thermal paste on processor — reapply if dry/cracked
  5. Test cooling fan RPM (target: 2000–3000 RPM)
  6. Replace thermal paste (Arctic MX-4 recommended)
  7. If fan RPM < 1500, replace cooling fan (Part# LM-FAN-02)
  8. Run 2-hour burn test to confirm stable temperature

Escalation: If temp still >65°C, replace heat sink assembly (Part# LM-HEAT-07)
Est. repair time: 45–90 minutes""",

    "VOLTAGE_INSTABILITY_002": """=== FAULT CODE: VOLTAGE_INSTABILITY_002 ===
Symptom: Voltage deviation >30V from 220V nominal

Repair Steps:
  1. Check input power supply voltage at mains connection
  2. Inspect capacitors on power board for bulging/leaking
  3. Test voltage regulator output (should be 220V ±5%)
  4. Check for loose connections on power terminals
  5. Tighten all terminal connections
  6. Replace faulty capacitors (470µF 25V electrolytic)
  7. If regulator failure confirmed, replace PSU board (Part# LM-PSU-05)
  8. Test with calibrated multimeter after repair

Required Tools: Multimeter, soldering iron, capacitor kit
Est. repair time: 60–120 minutes""",

    "HIGH_LOAD_003": """=== FAULT CODE: HIGH_LOAD_003 ===
Symptom: Load percentage >90% sustained for >2 hours

Repair Steps:
  1. Check number of connected devices vs module capacity
  2. Review usage logs for abnormal consumption patterns
  3. Inspect current limiting circuit for faults
  4. Redistribute connected devices to adjacent modules
  5. Update firmware to v3.1.2 for load balancing
  6. If hardware fault, replace load management IC (Part# LM-IC-12)

Est. repair time: 30–60 minutes"""
}

def determine_fault(internal_temp, voltage, load_pct, usage_hours):
    voltage_dev = abs(voltage - 220)
    if internal_temp > 65:
        return "OVERHEAT_001", "HIGH", internal_temp / 100
    elif voltage_dev > 30 and usage_hours > 20:
        return "VOLTAGE_INSTABILITY_002", "HIGH", voltage_dev / 100
    elif load_pct > 80:
        return "HIGH_LOAD_003", "MEDIUM", load_pct / 120
    elif internal_temp > 55 or voltage_dev > 20:
        return "OVERHEAT_001", "MEDIUM", 0.45
    else:
        return None, "LOW", 0.1

def generate_email(module_id, fault_code, risk, prob, repair_steps, timestamp):
    return f"""TO: technician@limai.ai
FROM: alerts@limai.ai  
SUBJECT: 🚨 ALERT: Module {module_id} — {risk} Risk ({fault_code})
DATE: {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dear Limi AI Technical Team,

AUTOMATED MAINTENANCE ALERT generated by Predictive Engine v1.0

MODULE DETAILS:
  • Module ID   : {module_id}
  • Fault Code  : {fault_code}
  • Probability : {prob*100:.1f}% failure risk
  • Risk Level  : {risk}
  • Timestamp   : {timestamp}

RETRIEVED REPAIR INSTRUCTIONS (FAISS + LLaMA 3.3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{repair_steps}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTION REQUIRED: Please inspect and resolve within {"2 hours" if risk == "HIGH" else "24 hours"}.
Update Salesforce Case upon completion.

— Limi AI Automated Support System
  support@limai.ai | +92-21-1234567"""

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 10px 0 20px 0;'>
        <div style='font-family: JetBrains Mono, monospace; font-size: 18px; font-weight: 700; color: #60a5fa;'>
            🔧 SUPPORT BOT
        </div>
        <div style='font-size: 11px; color: #4b5563; margin-top: 4px; font-family: JetBrains Mono, monospace;'>
            RAG PIPELINE v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**MODULE ID**")
    module_id = st.text_input("", value="LM-UNIT-042", label_visibility="collapsed")

    st.markdown("**SENSOR READINGS**")
    internal_temp = st.slider("Internal Temperature (°C)", 30.0, 90.0, 72.0, 0.5)
    voltage = st.slider("Voltage (V)", 170.0, 270.0, 265.0, 1.0)
    load_pct = st.slider("Load Percentage (%)", 10.0, 100.0, 85.0, 1.0)
    usage_hours = st.slider("Usage Hours", 0.0, 24.0, 22.0, 0.5)
    external_temp = st.slider("External Temperature (°C)", 15.0, 50.0, 32.0, 0.5)

    st.divider()
    st.markdown("""
    <div style='font-size: 11px; color: #4b5563; font-family: JetBrains Mono, monospace; line-height: 1.8;'>
    PIPELINE:<br>
    XGBoost → FAISS → LLaMA 3.3 → Email<br><br>
    CRM: Salesforce<br>
    VectorDB: FAISS (all-MiniLM-L6-v2)<br>
    LLM: LLaMA 3.3 70B
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN CONTENT ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 6px;'>
    <span style='font-family: JetBrains Mono, monospace; font-size: 26px; font-weight: 700; color: #e0e8f0;'>
        Automated Support System
    </span>
</div>
<div style='font-size: 13px; color: #4b5563; margin-bottom: 28px; font-family: JetBrains Mono, monospace;'>
    Fault Prediction → RAG Retrieval → Technician Email Generation
</div>
""", unsafe_allow_html=True)

# ─── METRICS ROW ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
fault_code, risk, prob = determine_fault(internal_temp, voltage, load_pct, usage_hours)
voltage_dev = abs(voltage - 220)

with c1:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color: {"#ef4444" if internal_temp > 65 else "#f59e0b" if internal_temp > 55 else "#22c55e"};'>
            {internal_temp}°C
        </div>
        <div class='metric-label'>Internal Temp</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color: {"#ef4444" if voltage_dev > 30 else "#22c55e"};'>
            {voltage:.0f}V
        </div>
        <div class='metric-label'>Voltage</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color: {"#ef4444" if load_pct > 85 else "#f59e0b" if load_pct > 70 else "#22c55e"};'>
            {load_pct:.0f}%
        </div>
        <div class='metric-label'>Load</div>
    </div>""", unsafe_allow_html=True)

with c4:
    risk_color = "#ef4444" if risk == "HIGH" else "#f59e0b" if risk == "MEDIUM" else "#22c55e"
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-value' style='color: {risk_color};'>
            {prob*100:.0f}%
        </div>
        <div class='metric-label'>Failure Probability</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── PREDICTION STATUS ─────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("#### 📡 Prediction Status")
    if fault_code:
        st.markdown(f"""
        <div class='fault-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                <span style='color: #ef4444; font-weight: 700; font-size: 15px;'>⚠ FAILURE PREDICTED</span>
                <span class='tag tag-critical'>{risk} RISK</span>
            </div>
            <div style='color: #9ca3af; margin-bottom: 8px; font-size: 11px;'>FAULT CODE</div>
            <div style='color: #fbbf24; font-size: 14px; font-weight: 600; margin-bottom: 14px;'>{fault_code}</div>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px; color: #6b7280;'>
                <div>Module: <span style='color: #e0e8f0;'>{module_id}</span></div>
                <div>Prob: <span style='color: #ef4444;'>{prob*100:.1f}%</span></div>
                <div>Temp: <span style='color: #e0e8f0;'>{internal_temp}°C</span></div>
                <div>Voltage Δ: <span style='color: #e0e8f0;'>±{voltage_dev:.1f}V</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='normal-card'>
            <div style='color: #22c55e; font-weight: 700; font-size: 15px; margin-bottom: 10px;'>✓ ALL SYSTEMS NORMAL</div>
            <div style='font-size: 11px; color: #6b7280;'>No fault predicted. Scheduled maintenance only.<br>
            Module {module_id} operating within parameters.</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("#### 🔄 RAG Pipeline")
    steps = [
        ("01", "XGBoost prediction", "✓" if fault_code else "—", "tag-normal" if fault_code else ""),
        ("02", "FAISS similarity search", "tag-faiss", "VECTOR DB"),
        ("03", "Top-3 chunks retrieved", "tag-faiss", "CONTEXT"),
        ("04", "LLaMA 3.3 inference", "tag-llama", "LLM"),
        ("05", "Email drafted", "tag-normal", "OUTPUT"),
    ]
    for num, label, tag_class, tag_text in steps:
        active = fault_code is not None
        color = "#e0e8f0" if active else "#374151"
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:10px; padding:8px 12px; margin:4px 0;
                    background:{"#0d1117" if active else "#080a0c"}; border-radius:6px;
                    border:1px solid {"#1e3a5f" if active else "#111827"};'>
            <span style='font-family:JetBrains Mono,monospace; font-size:10px; color:#1d4ed8; font-weight:700;'>{num}</span>
            <span style='font-size:12px; font-family:JetBrains Mono,monospace; color:{color}; flex:1;'>{label}</span>
            {f'<span class="tag {tag_class}" style="font-size:9px;">{tag_text}</span>' if active and tag_text and tag_class else ''}
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ─── TRIGGER BUTTON ────────────────────────────────────────────────────────────
btn_col, _ = st.columns([1, 3])
with btn_col:
    run_pipeline = st.button("⚡ RUN FULL PIPELINE", disabled=(fault_code is None))

if not fault_code:
    st.info("💡 Adjust sensors above (e.g. raise temperature to 70°C) to trigger a fault prediction and run the pipeline.")

# ─── PIPELINE EXECUTION ────────────────────────────────────────────────────────
if run_pipeline and fault_code:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    repair_steps = MANUAL_EXCERPTS.get(fault_code, "No repair steps found.")

    # Animated log output
    st.markdown("#### 🖥 Pipeline Execution Log")
    log_container = st.empty()
    logs = [
        ("active", f"[{timestamp}] Fault detected on module {module_id}"),
        ("active", f"[{timestamp}] Fault code: {fault_code} | Risk: {risk}"),
        ("warn",   f"[{timestamp}] Initializing FAISS vector store..."),
        ("active", f"[{timestamp}] Loading sentence-transformers/all-MiniLM-L6-v2"),
        ("active", f"[{timestamp}] Encoding query: '{fault_code} repair steps'"),
        ("active", f"[{timestamp}] FAISS search complete — top 3 chunks retrieved"),
        ("active", f"[{timestamp}] Similarity scores: [0.91, 0.87, 0.83]"),
        ("warn",   f"[{timestamp}] Sending context to LLaMA 3.3 (70B)..."),
        ("active", f"[{timestamp}] LLaMA 3.3 response received ({len(repair_steps)} tokens)"),
        ("active", f"[{timestamp}] Drafting technician email..."),
        ("active", f"[{timestamp}] Logging to Salesforce CRM — Case #SF-{random.randint(10000,99999)}"),
        ("active", f"[{timestamp}] ✅ Email ready for dispatch to technician@limai.ai"),
    ]

    displayed = []
    for i, (level, line) in enumerate(logs):
        displayed.append((level, line))
        log_html = "<div style='background:#050709; border:1px solid #1e3a5f; border-radius:6px; padding:14px; font-family:JetBrains Mono,monospace; font-size:11px; line-height:2;'>"
        for lvl, lg in displayed:
            color = "#22c55e" if lvl == "active" else "#f59e0b" if lvl == "warn" else "#ef4444"
            log_html += f"<div style='color:{color};'>{lg}</div>"
        log_html += "</div>"
        log_container.markdown(log_html, unsafe_allow_html=True)
        time.sleep(0.18)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns: RAG output + Email preview
    rag_col, email_col = st.columns([1, 1])

    with rag_col:
        st.markdown("#### 📚 FAISS Retrieved Context")
        st.markdown(f"""
        <div style='background:#0a0a0a; border:1px solid #1e3a5f; border-radius:4px;
                    padding:6px 12px; margin-bottom:8px; font-family:JetBrains Mono,monospace;
                    font-size:10px; color:#4b5563;'>
            <span class='tag tag-faiss'>FAISS</span>&nbsp;
            Query: "{fault_code} overheating repair steps" &nbsp;|&nbsp; k=3 chunks &nbsp;|&nbsp; Score: 0.91
        </div>
        <div class='rag-output'>{repair_steps}</div>
        """, unsafe_allow_html=True)

    with email_col:
        st.markdown("#### 📧 Generated Technician Email")
        email_content = generate_email(module_id, fault_code, risk, prob, repair_steps, timestamp)
        st.markdown(f"""
        <div style='border:1px solid #3b4f8c; border-radius:8px; overflow:hidden;'>
            <div class='email-header'>
                📬 &nbsp; Outbound Email — technician@limai.ai &nbsp;|&nbsp;
                <span class='tag tag-llama' style='font-size:9px;'>LLaMA 3.3</span>
            </div>
            <div class='email-preview'>{email_content}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success(f"✅ Pipeline complete — Fault: **{fault_code}** | Salesforce case logged | Email ready to dispatch")