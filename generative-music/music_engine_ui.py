import streamlit as st
import time
import random
import math
import os
import io
import wave
import tempfile
from typing import Optional
from datetime import datetime
from midiutil import MIDIFile

# Always resolve paths relative to this script's folder (works on Windows too)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── MODE CONFIG (must be defined before functions that use it) ────────────────
MODE_CONFIG_MIDI = {
    "focus":     {"tempo": 60,  "midi_program": 89, "note_duration": 1.0,  "volume_val": 60,
                  "note_sequence": [60,62,64,65,67,69,67,65,64,62,60,62,64,67,65,62]},
    "social":    {"tempo": 120, "midi_program": 11, "note_duration": 0.5,  "volume_val": 90,
                  "note_sequence": [60,63,65,67,70,72,70,67,65,63,60,63,67,70,65,60]},
    "energetic": {"tempo": 145, "midi_program": 80, "note_duration": 0.25, "volume_val": 110,
                  "note_sequence": [60,67,70,72,75,72,70,67,60,63,67,72,70,67,63,60]},
    "calm":      {"tempo": 45,  "midi_program": 48, "note_duration": 2.0,  "volume_val": 45,
                  "note_sequence": [60,64,67,72,67,64,60,62,65,69,65,62,60,64,67,60]},
}

# ─── AUDIO FUNCTIONS ──────────────────────────────────────────────────────────
def generate_midi_bytes(mode_key: str) -> bytes:
    """Generate a MIDI file for the given mode and return raw bytes."""
    cfg = MODE_CONFIG_MIDI[mode_key]
    midi = MIDIFile(1)
    track, channel = 0, 0
    midi.addTempo(track, 0, cfg["tempo"])
    midi.addProgramChange(track, channel, 0, cfg["midi_program"])

    notes    = cfg["note_sequence"]
    duration = cfg["note_duration"]
    vol      = cfg["volume_val"]

    time_pos     = 0.0
    beats_needed = int((cfg["tempo"] / 60) * 10)
    i = 0
    while time_pos < beats_needed:
        midi.addNote(track, channel, notes[i % len(notes)], time_pos, duration, vol)
        time_pos += duration
        i += 1

    tmp = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
    midi.writeFile(tmp)
    tmp.close()
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data


def synthesize_wav(mode_key: str) -> "Optional[bytes]":
    """
    Pure Python + numpy WAV synthesis.
    No FluidSynth, no pygame, no external tools needed.
    Returns WAV as bytes, or None if numpy is missing.
    """
    try:
        import numpy as np
    except ImportError:
        return None

    cfg      = MODE_CONFIG_MIDI[mode_key]
    notes    = cfg["note_sequence"]
    tempo    = cfg["tempo"]
    note_dur = cfg["note_duration"]        # beats
    volume   = cfg["volume_val"] / 127.0

    sample_rate  = 44100
    sec_per_beat = 60.0 / tempo
    note_sec     = note_dur * sec_per_beat
    n_notes      = max(1, int(10.0 / note_sec))  # fill 10 seconds

    chunks = []
    for i in range(n_notes):
        midi_note = notes[i % len(notes)]
        freq      = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        n_samp    = int(sample_rate * note_sec)
        t         = np.linspace(0.0, note_sec, n_samp, endpoint=False)

        # Sine + harmonics for a soft organ-like tone
        sig = (np.sin(2 * math.pi * freq * t) * 0.65 +
               np.sin(4 * math.pi * freq * t) * 0.20 +
               np.sin(6 * math.pi * freq * t) * 0.10 +
               np.sin(8 * math.pi * freq * t) * 0.05)

        # Simple ADSR envelope
        atk = min(int(0.02 * sample_rate), n_samp)
        rel = min(int(0.10 * sample_rate), n_samp)
        env = np.ones(n_samp)
        if atk > 0:
            env[:atk] = np.linspace(0.0, 1.0, atk)
        if rel > 0:
            env[n_samp - rel:] = np.linspace(1.0, 0.0, rel)

        chunks.append(sig * env * volume * 0.55)

    audio = np.clip(np.concatenate(chunks), -1.0, 1.0)
    pcm   = (audio * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Limi AI — Ambient Music Engine",
    layout="wide",
    page_icon="🎵",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;600;700;900&family=Fira+Code:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: #06030f;
    color: #ede9fe;
}

[data-testid="stSidebar"] {
    background: #09051a !important;
    border-right: 1px solid #1e1035;
}

h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700;
}

/* Animated visualizer bars */
.viz-container {
    display: flex;
    align-items: flex-end;
    gap: 4px;
    height: 80px;
    padding: 0 8px;
    justify-content: center;
}

@keyframes bar-focus {
    0%, 100% { height: 15px; }
    50% { height: 40px; }
}

@keyframes bar-social {
    0%, 100% { height: 60px; }
    25% { height: 20px; }
    75% { height: 70px; }
}

@keyframes bar-energetic {
    0%, 100% { height: 70px; }
    33% { height: 15px; }
    66% { height: 75px; }
}

@keyframes bar-calm {
    0%, 100% { height: 10px; }
    50% { height: 25px; }
}

@keyframes pulse-ring {
    0% { transform: scale(0.8); opacity: 1; }
    100% { transform: scale(2.5); opacity: 0; }
}

@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes float-up {
    0% { opacity: 0; transform: translateY(20px); }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { opacity: 0; transform: translateY(-60px); }
}

/* Mode cards */
.mode-card {
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
}

.mode-focus {
    background: linear-gradient(135deg, #0d0f1a 0%, #0a1628 100%);
    border-color: #2563eb;
}

.mode-social {
    background: linear-gradient(135deg, #0f0d1a 0%, #1a0a2a 100%);
    border-color: #9333ea;
}

.mode-energetic {
    background: linear-gradient(135deg, #1a0a0a 0%, #2a0a0a 100%);
    border-color: #ef4444;
}

.mode-calm {
    background: linear-gradient(135deg, #0a1a0a 0%, #0a2a1a 100%);
    border-color: #10b981;
}

.mode-card .mode-icon {
    font-size: 32px;
    margin-bottom: 8px;
    display: block;
}

.mode-card .mode-name {
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 4px;
}

.mode-card .mode-desc {
    font-size: 11px;
    opacity: 0.6;
    font-family: 'Fira Code', monospace;
}

/* Note display */
.note-seq {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    padding: 14px;
    background: #09051a;
    border-radius: 8px;
    border: 1px solid #1e1035;
    font-family: 'Fira Code', monospace;
}

.note-pill {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Fira Code', monospace;
}

.note-focus { background: #1e3a8a; color: #93c5fd; }
.note-social { background: #4c1d95; color: #c4b5fd; }
.note-energetic { background: #7f1d1d; color: #fca5a5; }
.note-calm { background: #064e3b; color: #6ee7b7; }

/* Waveform viz */
.waveform {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 60px;
    padding: 0 4px;
    overflow: hidden;
}

.wave-bar {
    border-radius: 2px;
    min-width: 4px;
    flex-shrink: 0;
}

/* MIDI info table */
.midi-table {
    background: #09051a;
    border: 1px solid #1e1035;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Fira Code', monospace;
    font-size: 12px;
}

.midi-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #1e1035;
    color: #a78bfa;
}

.midi-row:last-child { border-bottom: none; }
.midi-row .key { color: #6b7280; }

/* Prompt chat */
.chat-message {
    background: #0f0c1f;
    border: 1px solid #1e1035;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
}

.chat-user {
    border-left: 3px solid #9333ea;
    color: #c4b5fd;
}

.chat-bot {
    border-left: 3px solid #2563eb;
    color: #93c5fd;
    font-family: 'Fira Code', monospace;
    font-size: 12px;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 28px;
    cursor: pointer;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #9333ea, #a855f7);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(147,51,234,0.4);
}

.stTextInput > div > div > input {
    background: #0f0c1f !important;
    border: 1px solid #3b2f6b !important;
    border-radius: 8px !important;
    color: #ede9fe !important;
    font-family: 'Outfit', sans-serif !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: #0f0c1f !important;
    border-color: #3b2f6b !important;
}
</style>
""", unsafe_allow_html=True)

# ─── STATE ─────────────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "focus"
if "generated" not in st.session_state:
    st.session_state.generated = False
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

# ─── MUSIC ENGINE LOGIC ────────────────────────────────────────────────────────
MODE_CONFIG = {
    "focus": {
        "icon": "🧠", "color": "#2563eb", "bg": "#1e3a8a",
        "tempo": 60, "instrument": "Pad 2 (Warm)",
        "notes": ["C4","D4","E4","F4","G4","A4","C5","G4","E4","D4","C4","A3"],
        "note_class": "note-focus",
        "desc": "60 BPM · Low freq · Ambient loop",
        "waveform_color": "#3b82f6",
        "bar_heights": [15, 20, 18, 25, 20, 15, 22, 18, 15, 20, 25, 18, 15, 20, 18],
        "architecture": "LSTM (autoregressive, smooth transitions)",
        "volume": "60/127",
        "duration": "Whole beats (slow)"
    },
    "social": {
        "icon": "🎉", "color": "#9333ea", "bg": "#4c1d95",
        "tempo": 120, "instrument": "Vibraphone",
        "notes": ["C4","Eb4","F4","G4","Bb4","C5","G4","Eb4","F4","Bb3","C4","G4","Eb4","F4","C5"],
        "note_class": "note-social",
        "desc": "120 BPM · Mid-high freq · Groove",
        "waveform_color": "#a855f7",
        "bar_heights": [50, 30, 65, 20, 70, 45, 60, 25, 55, 70, 30, 65, 40, 55, 70],
        "architecture": "Transformer (fine-tuned on jazz/funk)",
        "volume": "90/127",
        "duration": "Quarter notes (medium)"
    },
    "energetic": {
        "icon": "⚡", "color": "#ef4444", "bg": "#7f1d1d",
        "tempo": 145, "instrument": "Lead 1 (Square)",
        "notes": ["C5","G4","Bb4","C5","Eb5","F5","G5","Eb5","C5","G4","Bb4","Eb5","F5","G5","C5"],
        "note_class": "note-energetic",
        "desc": "145 BPM · High freq · Driving",
        "waveform_color": "#f87171",
        "bar_heights": [70, 15, 75, 10, 72, 18, 68, 12, 73, 16, 70, 14, 75, 11, 70],
        "architecture": "Transformer (fine-tuned on electronic/dance)",
        "volume": "110/127",
        "duration": "Eighth notes (fast)"
    },
    "calm": {
        "icon": "🌊", "color": "#10b981", "bg": "#064e3b",
        "tempo": 45, "instrument": "String Ensemble",
        "notes": ["C4","E4","G4","C4","A3","E4","G3","C4","E4","G4","A4","G4","E4","C4"],
        "note_class": "note-calm",
        "desc": "45 BPM · Very low freq · Meditative",
        "waveform_color": "#34d399",
        "bar_heights": [8, 12, 10, 15, 8, 12, 10, 8, 13, 10, 8, 12, 9, 11, 8],
        "architecture": "LSTM (bidirectional, smooth arpeggios)",
        "volume": "45/127",
        "duration": "Half notes (very slow)"
    }
}

KEYWORD_MAP = {
    "energetic": ["energetic", "energy", "fast", "pump", "hype", "dance", "party hard", "upbeat", "loud", "intense"],
    "social": ["social", "party", "friends", "gathering", "fun", "celebrate", "people", "group", "vibe"],
    "focus": ["focus", "study", "work", "concentrate", "code", "think", "quiet", "productive", "deep work"],
    "calm": ["calm", "relax", "sleep", "rest", "meditate", "peaceful", "chill", "soothe", "unwind"]
}

def detect_mode(prompt):
    prompt_lower = prompt.lower()
    for mode, keywords in KEYWORD_MAP.items():
        if any(k in prompt_lower for k in keywords):
            return mode
    return "focus"

def generate_waveform_html(mode_key, animated=True):
    cfg = MODE_CONFIG[mode_key]
    color = cfg["waveform_color"]
    bars_html = ""
    for i, h in enumerate(cfg["bar_heights"]):
        delay = i * 0.08
        if animated:
            bars_html += f"""<div style='width:6px; height:{h}px; background:{color};
                border-radius:3px; animation: bar-{mode_key} {0.8 + (i%3)*0.3}s ease-in-out {delay}s infinite alternate;
                opacity:{0.5 + (h/150):.2f};'></div>"""
        else:
            bars_html += f"""<div style='width:6px; height:{h}px; background:{color};
                border-radius:3px; opacity:{0.5 + (h/150):.2f};'></div>"""
    return f"<div class='waveform'>{bars_html}</div>"

def generate_note_pills(mode_key):
    cfg = MODE_CONFIG[mode_key]
    pills = ""
    for note in cfg["notes"]:
        pills += f"<span class='note-pill {cfg['note_class']}'>{note}</span>"
    return f"<div class='note-seq'>{pills}</div>"

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 10px 0 20px 0;'>
        <div style='font-family: Outfit, sans-serif; font-size: 20px; font-weight: 900; color: #a78bfa;'>
            🎵 MUSIC ENGINE
        </div>
        <div style='font-size: 11px; color: #4b5563; margin-top: 4px; font-family: Fira Code, monospace;'>
            LSTM + TRANSFORMER v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**ROOM MODE**")
    mode_select = st.selectbox(
        "", ["focus", "social", "energetic", "calm"],
        index=["focus", "social", "energetic", "calm"].index(st.session_state.current_mode),
        label_visibility="collapsed"
    )
    st.session_state.current_mode = mode_select

    st.divider()
    cfg = MODE_CONFIG[mode_select]
    st.markdown(f"""
    <div style='font-family: Fira Code, monospace; font-size: 11px; color: #6b7280; line-height: 2;'>
    Tempo: <span style='color: {cfg["color"]};'>{cfg["tempo"]} BPM</span><br>
    Instrument: <span style='color: {cfg["color"]};'>{cfg["instrument"]}</span><br>
    Volume: <span style='color: {cfg["color"]};'>{cfg["volume"]}</span><br>
    Model: <span style='color: {cfg["color"]};'>{"LSTM" if mode_select in ["focus","calm"] else "Transformer"}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style='font-size: 11px; color: #4b5563; font-family: Fira Code, monospace; line-height: 1.8;'>
    MIDI Output: .mid<br>
    Duration: 10 seconds<br>
    LangChain: NLP → mode
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 6px;'>
    <span style='font-size: 28px; font-weight: 900; color: #ede9fe;'>
        Ambient Music Engine
    </span>
</div>
<div style='font-size: 13px; color: #4b5563; margin-bottom: 28px; font-family: Fira Code, monospace;'>
    LSTM · Transformer · LangChain → MIDI Generation
</div>
""", unsafe_allow_html=True)

# ─── MODE CARDS ────────────────────────────────────────────────────────────────
st.markdown("#### Room State Selector")
cols = st.columns(4)
mode_keys = ["focus", "social", "energetic", "calm"]
for i, (col, mk) in enumerate(zip(cols, mode_keys)):
    with col:
        cfg_c = MODE_CONFIG[mk]
        selected = (st.session_state.current_mode == mk)
        border = f"3px solid {cfg_c['color']}" if selected else "2px solid transparent"
        glow = f"box-shadow: 0 0 20px {cfg_c['color']}44;" if selected else ""
        st.markdown(f"""
        <div class='mode-card mode-{mk}' style='border: {border}; {glow}'>
            <span class='mode-icon'>{cfg_c['icon']}</span>
            <div class='mode-name' style='color: {cfg_c["color"]};'>{mk.upper()}</div>
            <div class='mode-desc'>{cfg_c['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Select", key=f"mode_{mk}"):
            st.session_state.current_mode = mk
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── LANGCHAIN PROMPT ──────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown("#### 💬 LangChain Prompt Interface")
    st.markdown("""
    <div style='font-size: 12px; color: #6b7280; margin-bottom: 10px; font-family: Fira Code, monospace;'>
    Type a natural language command → LangChain detects room state → generates music
    </div>
    """, unsafe_allow_html=True)

    prompt_input = st.text_input(
        "",
        placeholder='e.g. "Make the music more energetic, we\'re having a party!"',
        label_visibility="collapsed"
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        send_prompt = st.button("🤖 Send to LangChain")
    with col_b:
        generate_btn = st.button(f"🎵 Generate {st.session_state.current_mode.upper()} Music")

    # Chat history display
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history[-4:]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class='chat-message chat-user'>
                    👤 &nbsp;<strong>You:</strong> {msg["content"]}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-message chat-bot'>
                    🤖 &nbsp;{msg["content"]}
                </div>""", unsafe_allow_html=True)

with right_col:
    st.markdown("#### 🎚 Live Waveform")
    current_cfg = MODE_CONFIG[st.session_state.current_mode]
    st.markdown(f"""
    <div style='background:#09051a; border:1px solid #1e1035; border-radius:10px; padding:20px;'>
        <div style='text-align:center; margin-bottom:12px;'>
            <span style='font-size:36px;'>{current_cfg["icon"]}</span>
            <div style='font-size:14px; font-weight:700; color:{current_cfg["color"]}; margin-top:6px;'>
                {st.session_state.current_mode.upper()} MODE
            </div>
        </div>
        {generate_waveform_html(st.session_state.current_mode, animated=st.session_state.generated)}
        <div style='text-align:center; margin-top:10px; font-size:11px; color:#4b5563; font-family:Fira Code,monospace;'>
            {current_cfg["tempo"]} BPM · {current_cfg["instrument"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── HANDLE LANGCHAIN PROMPT ───────────────────────────────────────────────────
if send_prompt and prompt_input:
    detected = detect_mode(prompt_input)
    st.session_state.current_mode = detected
    cfg_d = MODE_CONFIG[detected]

    user_msg = {"role": "user", "content": prompt_input}
    bot_response = (
        f"STATE: {detected.upper()}\n"
        f"REASON: Detected '{detected}' intent from prompt keywords.\n"
        f"→ Switching to {detected} mode | {cfg_d['tempo']} BPM | {cfg_d['instrument']}\n"
        f"→ Architecture: {cfg_d['architecture']}\n"
        f"→ Generating MIDI sequence..."
    )
    bot_msg = {"role": "assistant", "content": bot_response}

    st.session_state.chat_history.extend([user_msg, bot_msg])
    st.session_state.generated = True
    st.session_state.generation_count += 1
    st.rerun()

# ─── HANDLE GENERATE BUTTON ────────────────────────────────────────────────────
if generate_btn:
    mode = st.session_state.current_mode
    cfg_g = MODE_CONFIG[mode]

    st.markdown("---")
    st.markdown(f"#### ⚙️ Generating {mode.upper()} Music...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    gen_steps = [
        (10, f"Initializing {'LSTM' if mode in ['focus','calm'] else 'Transformer'} model..."),
        (25, f"Loading {cfg_g['instrument']} instrument preset..."),
        (40, f"Seeding note sequence from {mode} mode scale..."),
        (60, f"Running {'autoregressive LSTM inference' if mode in ['focus','calm'] else 'Transformer attention pass'}..."),
        (75, f"Applying tempo ({cfg_g['tempo']} BPM) and dynamics..."),
        (90, f"Writing MIDI events to {mode}_generated.mid..."),
        (100, f"✅ Done! {mode}_generated.mid ready (10 seconds, {cfg_g['tempo']} BPM)"),
    ]

    for pct, msg in gen_steps:
        progress_bar.progress(pct)
        status_text.markdown(f"<span style='font-family:Fira Code,monospace; font-size:12px; color:#a78bfa;'>{msg}</span>", unsafe_allow_html=True)
        time.sleep(0.3)

    # ── Generate real MIDI bytes ──────────────────────────────────────────────
    midi_bytes = generate_midi_bytes(mode)

    # ── Synthesize WAV using pure Python + numpy (no external tools needed) ───
    status_text.markdown(
        "<span style='font-family:Fira Code,monospace; font-size:12px; color:#a78bfa;'>"
        "🔊 Synthesizing audio (numpy)...</span>",
        unsafe_allow_html=True
    )
    wav_bytes = synthesize_wav(mode)

    st.session_state.generated = True
    st.session_state.generation_count += 1
    st.session_state["last_midi"] = midi_bytes
    st.session_state["last_wav"]  = wav_bytes
    st.session_state["last_mode"] = mode

    # Results section
    st.markdown("<br>", unsafe_allow_html=True)
    res1, res2 = st.columns([1, 1])

    with res1:
        st.markdown("#### 🎹 Generated Note Sequence")
        st.markdown(generate_note_pills(mode), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 MIDI File Info")
        st.markdown(f"""
        <div class='midi-table'>
            <div class='midi-row'><span class='key'>File</span><span>{mode}_generated.mid</span></div>
            <div class='midi-row'><span class='key'>Duration</span><span>10 seconds</span></div>
            <div class='midi-row'><span class='key'>Tempo</span><span>{cfg_g['tempo']} BPM</span></div>
            <div class='midi-row'><span class='key'>Instrument</span><span>{cfg_g['instrument']}</span></div>
            <div class='midi-row'><span class='key'>Volume</span><span>{cfg_g['volume']}</span></div>
            <div class='midi-row'><span class='key'>Note Duration</span><span>{cfg_g['duration']}</span></div>
            <div class='midi-row'><span class='key'>Architecture</span><span style='color:{cfg_g["color"]};'>{"LSTM" if mode in ["focus","calm"] else "Transformer"}</span></div>
            <div class='midi-row'><span class='key'>Total Notes</span><span>{len(cfg_g['notes'])}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Download buttons ──────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download MIDI (.mid)",
            data=midi_bytes,
            file_name=f"{mode}_generated.mid",
            mime="audio/midi",
        )
        if wav_bytes:
            st.download_button(
                label="⬇️ Download WAV (.wav)",
                data=wav_bytes,
                file_name=f"{mode}_generated.wav",
                mime="audio/wav",
            )

    with res2:
        st.markdown("#### 🔊 Audio Player")

        if wav_bytes:
            # ── Real audio playback ───────────────────────────────────────────
            st.audio(wav_bytes, format="audio/wav")
            st.markdown(f"""
            <div style='background:#09051a; border:1px solid #1e1035; border-radius:8px;
                        padding:14px; margin-top:10px;'>
                {generate_waveform_html(mode, animated=True)}
                <div style='text-align:center; margin-top:10px; font-size:11px;
                            color:#4b5563; font-family:Fira Code,monospace;'>
                    ▶ {mode.upper()} MODE · {cfg_g['tempo']} BPM · {cfg_g['instrument']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # ── Fallback: no FluidSynth installed ────────────────────────────
            sf_path_display = os.path.join(SCRIPT_DIR, "soundfont.sf2").replace("\\", "\\\\")
            st.markdown(f"""
            <div style='background:#1a1005; border:1px solid #78350f; border-radius:8px; padding:16px;
                        font-family:Fira Code,monospace; font-size:12px; color:#fbbf24; line-height:2;'>
                ⚠ Audio synthesis failed.<br><br>
                <strong style='color:#e0e8f0;'>Quick fix — install numpy (1 package):</strong><br>
                <span style='color:#86efac;'>pip install numpy</span><br><br>
                Then restart Streamlit. Audio will play directly in the browser.<br><br>
                ✅ MIDI file ready — use the download button below to play in VLC or any media player.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            # Animated waveform still shown
            st.markdown(f"""
            <div style='background:#09051a; border:1px solid #1e1035; border-radius:8px; padding:14px;'>
                {generate_waveform_html(mode, animated=True)}
                <div style='text-align:center; margin-top:10px; font-size:11px;
                            color:#4b5563; font-family:Fira Code,monospace;'>
                    {mode.upper()} · {cfg_g['tempo']} BPM · MIDI ready
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏗 Model Architecture")
        arch_steps = [
            ("01", "Seed: first 3 notes from scale"),
            ("02", f"{'LSTM cell: hidden state h(t)' if mode in ['focus','calm'] else 'Transformer: multi-head attention'}"),
            ("03", "Next-note probability distribution"),
            ("04", f"{'Smooth sampling (low temp)' if mode in ['focus','calm'] else 'Diverse sampling (high temp)'}"),
            ("05", "MIDI note + velocity + duration → .wav"),
        ]
        for num, label in arch_steps:
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:10px; padding:6px 12px; margin:3px 0;
                        background:#09051a; border-radius:5px; border:1px solid #1e1035;'>
                <span style='font-family:Fira Code,monospace; font-size:10px; color:{cfg_g["color"]}; font-weight:700;'>{num}</span>
                <span style='font-size:11px; font-family:Fira Code,monospace; color:#a78bfa;'>{label}</span>
            </div>
            """, unsafe_allow_html=True)

    audio_status = "🔊 Audio playable in browser" if wav_bytes else "📁 MIDI generated (install FluidSynth for audio)"
    st.success(f"✅ **{mode.upper()} music generated!** {audio_status} | Sessions: {st.session_state.generation_count}")

# ─── FOOTER STATS ──────────────────────────────────────────────────────────────
st.divider()
f1, f2, f3, f4 = st.columns(4)
stats = [
    ("Sessions", st.session_state.generation_count),
    ("Active Mode", st.session_state.current_mode.upper()),
    ("Architecture", "LSTM" if st.session_state.current_mode in ["focus","calm"] else "Transformer"),
    ("Status", "READY" if not st.session_state.generated else "GENERATED")
]
for col, (label, val) in zip([f1,f2,f3,f4], stats):
    with col:
        color = MODE_CONFIG[st.session_state.current_mode]["color"]
        st.markdown(f"""
        <div style='background:#09051a; border:1px solid #1e1035; border-radius:6px;
                    padding:10px; text-align:center;'>
            <div style='font-family:Fira Code,monospace; font-size:14px; font-weight:700; color:{color};'>{val}</div>
            <div style='font-size:10px; color:#4b5563; text-transform:uppercase; letter-spacing:1px; margin-top:3px;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)
