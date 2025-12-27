import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

# --- 1. High-Contrast Athletic Theme ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #F8FAFC; color: #1E293B; }
    
    /* DRILL NAME - BLUE ACCENT VERSION */
    .drill-header {
        font-size: 32px !important; 
        font-weight: 900 !important; 
        color: #000000 !important; /* Pure Black text */
        margin-top: 40px; 
        margin-bottom: 15px;
        background-color: #EFF6FF; /* Soft Blue Tint background */
        border-left: 12px solid #2563EB; /* Electric Blue border */
        padding: 15px 25px;
        border-radius: 8px;
        display: block;
        width: 100%;
        letter-spacing: 1px;
    }
    
    /* High-Visibility Rest Timer */
    .timer-text {
        font-size: 80px !important; 
        font-weight: 800 !important; 
        color: #2563EB !important; 
        text-align: center; 
        background: #FFFFFF; 
        border-radius: 20px; 
        padding: 20px;
        border: 4px solid #2563EB;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 2px solid #DBEAFE;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    /* Action Buttons */
    .stButton>button { 
        background-color: #2563EB; 
        color: white; 
        border-radius: 10px; 
        font-weight: 700; 
        height: 60px; 
        font-size: 20px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Logic & Session Data ---
if 'set_counters' not in st.session_state: st.session_state.set_counters = {}
if 'streak' not in st.session_state: st.session_state.streak = 1

def get_drills():
    return [
        {"ex": "POUND SERIES", "base": 30, "sets": 4, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "note": "Maintain a low, athletic stance. Hard, violent dribbles."},
        {"ex": "MIKAN SERIES", "base": 25, "sets": 4, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "note": "Focus on high, soft-touch finishes. Do not let the ball drop below your chin."},
        {"ex": "STATIONARY CROSSOVER", "base": 50, "sets": 4, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "note": "Wide crossovers outside your frame. Snap the ball across."}
    ]

# --- 3. Sidebar Customization ---
st.sidebar.title("🥇 Athlete Profile")
st.sidebar.metric("Current Streak", f"{st.session_state.streak} Days")

st.sidebar.markdown("---")
st.sidebar.subheader("Timer Settings")
# Rest customizer requested by user
rest_seconds = st.sidebar.slider("Rest Duration (Seconds)", min_value=15, max_value=120, value=30, step=15)

difficulty = st.sidebar.select_slider("Workout Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
target_mult = 1.0 if difficulty == "Standard" else 1.5 if difficulty == "Elite" else 2.0

# --- 4. Main App UI ---
st.title("Performance Tracker")
all_drills = get_drills()

for i, drill in enumerate(all_drills):
    drill_key = f"drill_{i}"
    if drill_key not in st.session_state.set_counters: st.session_state.set_counters[drill_key] = 0
    
    # Drill Header with User-Requested Blue Theme
    st.markdown(f'<div class="drill-header">{drill["ex"]}</div>', unsafe_allow_html=True)
    
    current = st.session_state.set_counters[drill_key]
    st.info(f"Progress: Set {current} of {drill['sets']} Completed")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        reps = int(drill['base'] * target_mult)
        st.metric("Target Reps", f"{reps}")
        if st.button(f"Complete Set", key=f"btn_{i}"):
            st.session_state.set_counters[drill_key] = min(current + 1, drill['sets'])
            st.rerun()
            
    with c2:
        if st.button(f"Start Rest", key=f"t_{i}"):
            placeholder = st.empty()
            for seconds in range(rest_seconds, -1, -1):
                placeholder.markdown(f'<p class="timer-text">{seconds}s</p>', unsafe_allow_html=True)
                time.sleep(1)
            # Auto-increment set after rest finishes
            st.session_state.set_counters[drill_key] = min(current + 1, drill['sets'])
            st.rerun()
            
    with c3:
        st.number_input("Log Actual", key=f"val_{i}", min_value=0)
        st.select_slider("Intensity (1-10)", options=range(1,11), value=8, key=f"rpe_{i}")

    with st.expander("🎥 View Form Demo & Coach's Checklist"):
        st.markdown(f"**Coach's Note:** *{drill['note']}*")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("**PRO DEMO**")
            st.video(drill['vid'])
        with v_col2:
            st.markdown("**YOUR CLIP**")
            up = st.file_uploader("Upload from Gallery", type=["mp4", "mov"], key=f"up_{i}")
            if up: st.video(up)

st.divider()

if st.button("Finish & Save Workout"):
    st.balloons()
    st.success("Session saved! Your consistency is building elite results.")
