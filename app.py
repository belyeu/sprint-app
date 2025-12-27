import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. High-Visibility Theme Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Initialize Dark Mode in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Sidebar Toggle for Dark Mode
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors based on Mode
if dark_mode:
    bg_color = "#0F172A"        # Deep Navy
    card_bg = "#1E293B"         # Slate Gray
    text_color = "#FFFFFF"      # Pure White
    accent_color = "#38BDF8"    # Vivid Sky Blue
    header_bg = "#334155"       # Medium Slate
    sidebar_text = "#FFFFFF"    # Unified Sidebar Font: White
else:
    bg_color = "#F8FAFC"        # Bright White-Gray
    card_bg = "#FFFFFF"         # Pure White
    text_color = "#0F172A"      # Deep Slate Text
    accent_color = "#2563EB"    # Royal Blue
    header_bg = "#E2E8F0"       # Light Steel Gray
    sidebar_text = "#0F172A"    # Unified Sidebar Font: Dark Navy

st.markdown(f"""
    <style>
    /* Global Styles */
    .main {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    /* UNIFIED SIDEBAR FONT COLOR - Targets all elements */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stSelectbox p,
    [data-testid="stSidebar"] .stNumberInput label {{
        color: {sidebar_text} !important;
    }}

    /* Drill Section Styling */
    .drill-header {{
        font-size: 32px !important;
        font-weight: 900 !important;
        color: {accent_color} !important;
        text-transform: uppercase;
        margin-bottom: 10px;
        margin-top: 35px;
        font-family: 'Arial Black', sans-serif;
        border-left: 12px solid {accent_color};
        padding: 15px 20px;
        background-color: {header_bg};
        border-radius: 0 10px 10px 0;
    }}
    
    .stat-label {{ font-size: 18px !important; font-weight: 800 !important; color: {accent_color} !important; text-transform: uppercase; }}
    .stat-value {{ font-size: 42px !important; font-weight: 900 !important; color: {text_color} !important; }}

    .timer-text {{
        font-size: 85px !important;
        font-weight: bold !important;
        color: {accent_color} !important;
        text-align: center;
        font-family: 'Courier New', monospace;
        background: {bg_color};
        border-radius: 12px;
        border: 5px solid {accent_color};
        padding: 15px;
        margin: 10px 0;
    }}

    .stButton>button {{ 
        background-color: {accent_color} !important; 
        color: white !important; 
        border-radius: 12px !important; 
        font-weight: 900 !important; 
        width: 100%; 
        height: 75px !important;
        font-size: 24px !important;
        border: none !important;
    }}

    /* Sidebar Streak Card Styling */
    .sidebar-card {{
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 3px solid {accent_color};
    }}

    @media (max-width: 600px) {{
        .timer-text {{ font-size: 55px !important; }}
        .stat-value {{ font-size: 32px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Multi-Sport Drill Database (Full Integrity) ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "base": 60, "inc": 15, "unit": "sec", "rest": 30, "type": "cond", "desc": "Hard, explosive dribbles at hip, knee, and ankle height. Keep eyes up.", "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Power Dribble", "Eyes Up"]},
            {"ex": "FIGURE 8 SERIES", "base": 90, "inc": 20, "unit": "sec", "rest": 30, "type": "cond", "desc": "Low dribbles in a figure-8 pattern around legs.", "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Fingertip Control", "Low Center", "No Tangles"]},
            {"ex": "STATIONARY CROSSOVER", "base": 100, "inc": 25, "unit": "reps", "rest": 45, "type": "power", "desc": "Wide crossovers outside the body frame. Snap the ball.", "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "eval": ["Wide Snap", "Rhythm", "Low Hips"]},
            {"ex": "MIKAN SERIES", "base": 50, "inc": 10, "unit": "makes", "rest": 60, "type": "power", "desc": "Continuous layups alternating hands. Keep ball high.", "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["High Finish", "Footwork", "Soft Touch"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "base": 40, "inc": 10, "unit": "meters", "rest": 30, "type": "cond", "desc": "Quick steps with toes up. Movement from ankles.", "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Ankle Drive", "Tall Posture"]},
            {"ex": "A-SKIP", "base": 60, "inc": 10, "unit": "meters", "rest": 60, "type": "power", "desc": "Aggressive foot strike under center of mass.", "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Action", "Knee Drive"]}
        ],
        "Softball": [
            {"ex": "TEE SERIES", "base": 50, "inc": 15, "unit": "swings", "rest": 60, "type": "power", "desc": "Focus on hand path. Hit to all fields.", "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact", "Balanced Stance"]},
            {"ex": "GLOVE WORK", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power", "desc": "Develop soft hands and quick transfers.", "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Soft Hands", "Quick Transfer", "Glove Position"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "base": 15, "inc": 3, "unit": "reps", "rest": 120, "type": "power", "desc": "Hold weight at chest. Sit back into hips.", "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up", "Heels Down"]},
            {"ex": "PUSHUPS", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power", "desc": "Full range of motion. Chest to floor.", "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout", "Chest to Floor"]}
        ]
    }
    return workouts.get(sport, [])

# --- 3. Sidebar Profile ---
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
if 'streak' not in st.session_state: st.session_state.streak = 1
st.sidebar.markdown(f'<p style="margin:0; font-weight:800; font-size:16px;">STREAK</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="font-size:44px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 4. Main App UI ---
st.markdown(f"<h1>{sport_choice} Tracker</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

if 'session_saved' not in st.session_state: st.session_state.session_saved = False

for i, item in enumerate(drills):
    drill_key = f"{sport_choice}_{i}"
    if drill_key not in st.session_state: st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        target_val = int((item['base'] + ((week_num - 1) * item['inc'])) * target_mult)
        st.markdown(f'<p class="stat-label">Target</p><p class="stat-value">{target_val} {item["unit"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="stat-label">Sets Done</p><p class="stat-value">{st.session_state[drill_key]}</p>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"DONE ✅", key=f"done_{i}"):
            st.session_state[drill_key] += 1
            st.rerun()
    with col_b:
        if st.button(f"REST ⏱️", key=f"rest_{i}"):
            final_rest = int(item['rest'] * rest_mult) if item['type'] == 'power' else int(item['rest'] / rest_mult)
            ph = st.empty()
            for t in range(final_rest, -1, -1):
                m, s = divmod(t, 60)
                ph.markdown(f'<p class="timer-text">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state[drill_key] += 1
            st.rerun()

    with st.expander("🎥 DRILL DEMO & NOTES"):
        st.video(item['vid'])
        st.markdown(f"**Focus:** {item['desc']}")

st.divider()
if st.button("💾 SAVE WORKOUT"):
    st.balloons()
    st.session_state.streak += 1
    st.success("Session saved! Streak updated.")
