import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. High-Visibility Theme Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Initialize Session State
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'session_saved' not in st.session_state: 
    st.session_state.session_saved = False

# Sidebar Toggle for Dark Mode
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors
if dark_mode:
    bg_color = "#0F172A"        
    text_color = "#FFFFFF"      
    accent_color = "#38BDF8"    
    header_bg = "#334155"       
    sidebar_text = "#FFFFFF"    
else:
    bg_color = "#F8FAFC"        
    text_color = "#0F172A"      
    accent_color = "#2563EB"    
    header_bg = "#E2E8F0"       
    sidebar_text = "#0F172A"    

st.markdown(f"""
    <style>
    .main {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: {sidebar_text} !important;
    }}

    .drill-header {{
        font-size: 30px !important;
        font-weight: 900 !important;
        color: {accent_color} !important;
        text-transform: uppercase;
        margin-top: 35px;
        border-left: 12px solid {accent_color};
        padding: 10px 20px;
        background-color: {header_bg};
        border-radius: 0 10px 10px 0;
    }}
    
    .stat-label {{ font-size: 16px !important; font-weight: 800 !important; color: {accent_color} !important; text-transform: uppercase; }}
    .stat-value {{ font-size: 38px !important; font-weight: 900 !important; color: {text_color} !important; margin-bottom: 15px; }}

    .timer-text {{
        font-size: 75px !important;
        font-weight: bold !important;
        color: {accent_color} !important;
        text-align: center;
        font-family: 'Courier New', monospace;
        background: {bg_color};
        border-radius: 12px;
        border: 4px solid {accent_color};
        padding: 10px;
        margin: 10px 0;
    }}

    .stButton>button {{ 
        background-color: {accent_color} !important; 
        color: white !important; 
        border-radius: 12px !important; 
        font-weight: 900 !important; 
        width: 100%; 
        height: 65px !important;
        font-size: 20px !important;
        border: none !important;
    }}

    .sidebar-card {{
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid {accent_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Multi-Sport Drill Database ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "base": 60, "inc": 15, "unit": "sec", "rest": 30, "type": "cond", "desc": "Explosive dribbles at hip/knee/ankle height.", "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Power Dribble", "Eyes Up"]},
            {"ex": "FIGURE 8 SERIES", "base": 90, "inc": 20, "unit": "sec", "rest": 30, "type": "cond", "desc": "Low dribbles in figure-8 pattern.", "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Fingertip Control", "Low Center", "No Tangles"]},
            {"ex": "MIKAN SERIES", "base": 50, "inc": 10, "unit": "makes", "rest": 60, "type": "power", "desc": "Continuous alternating layups.", "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["High Finish", "Footwork", "Soft Touch"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "base": 40, "inc": 10, "unit": "meters", "rest": 30, "type": "cond", "desc": "Quick steps, toes up.", "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Ankle Drive", "Tall Posture"]},
            {"ex": "A-SKIP", "base": 60, "inc": 10, "unit": "meters", "rest": 60, "type": "power", "desc": "Aggressive strike under center.", "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Action", "Knee Drive"]}
        ],
        "Softball": [
            {"ex": "TEE SERIES", "base": 50, "inc": 15, "unit": "swings", "rest": 60, "type": "power", "desc": "Focus on hand path.", "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact", "Balanced Stance"]},
            {"ex": "GLOVE WORK", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power", "desc": "Soft hands/quick transfers.", "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Soft Hands", "Quick Transfer", "Glove Position"]}
        ]
    }
    return workouts.get(sport, [])

# --- 3. Sidebar Profile ---
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="margin:0; font-weight:800; font-size:14px;">STREAK</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="font-size:36px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 4. Main App UI ---
st.markdown(f"<h1>{sport_choice} Performance</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

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

    # Action Row
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

    # RESTORED: Coach's Evaluation Section
    st.markdown("### 📋 COACH'S EVALUATION")
    eval_cols = st.columns(2)
    for idx, criteria in enumerate(item['eval']):
        eval_cols[idx % 2].checkbox(criteria, key=f"eval_check_{drill_key}_{idx}")
    
    st.select_slider(f"Drill Intensity (RPE 1-10)", options=range(1, 11), value=8, key=f"rpe_{drill_key}")
    st.text_input("Coach's Notes / Feedback", key=f"notes_{drill_key}", placeholder="Enter specific feedback here...")

    with st.expander("🎥 DRILL DEMO & UPLOAD"):
        st.video(item['vid'])
        st.file_uploader("Upload Practice Clip", type=["mp4", "mov"], key=f"up_{i}")

st.divider()
if st.button("💾 SAVE WORKOUT"):
    st.balloons()
    st.session_state.streak += 1
    st.session_state.session_saved = True
    st.success("Session saved! Streak updated.")

if st.session_state.session_saved:
    st.info("Recovery Protocol: 1. Hydrate 2. Protein Intake 3. Stretch.")
