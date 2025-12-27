import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

# --- 1. Inviting Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; color: #1E293B; }
    .drill-header {
        font-size: 28px !important; font-weight: 800 !important; color: #0F172A !important;
        text-transform: capitalize; margin-top: 25px; font-family: 'Inter', sans-serif;
        border-left: 6px solid #3B82F6; padding-left: 15px;
    }
    .timer-text {
        font-size: 70px !important; font-weight: 700 !important; color: #3B82F6 !important;
        text-align: center; font-family: 'Monaco', monospace;
        background: #EFF6FF; border-radius: 16px; border: 2px solid #DBEAFE; padding: 10px;
    }
    .set-badge {
        background-color: #10B981; color: white; padding: 6px 16px;
        border-radius: 20px; font-weight: 600; font-size: 14px; 
        display: inline-block; margin-bottom: 10px;
    }
    .coach-eval {
        background-color: #F1F5F9; border: 1px solid #CBD5E1;
        padding: 20px; border-radius: 12px; margin-top: 15px;
    }
    .stButton>button { 
        background-color: #3B82F6; color: white; border-radius: 8px; 
        font-weight: 600; border: none; width: 100%; height: 50px; font-size: 18px;
    }
    .stMetric { 
        background-color: white; padding: 15px; border-radius: 12px; 
        border: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State Initialization ---
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'last_workout' not in st.session_state: st.session_state.last_workout = None
if 'set_counters' not in st.session_state: st.session_state.set_counters = {}
if 'session_history' not in st.session_state: st.session_state.session_history = {}

# --- 3. Helper Functions ---
def update_streak():
    today = date.today()
    if st.session_state.last_workout is None:
        st.session_state.streak = 1
    else:
        diff = (today - st.session_state.last_workout).days
        if diff == 1: st.session_state.streak += 1
        elif diff > 1: st.session_state.streak = 1
    st.session_state.last_workout = today

def get_workout_template():
    return [
        {"ex": "Pound Series", "base_reps": 30, "sets": 4, "inc": 5, "unit": "sec", "pro_bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
        {"ex": "Mikan Series", "base_reps": 25, "sets": 4, "inc": 5, "unit": "makes", "pro_bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"},
        {"ex": "Stationary Crossover", "base_reps": 50, "sets": 4, "inc": 10, "unit": "reps", "pro_bench": 400, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E"}
    ]

# --- 4. Sidebar ---
st.sidebar.markdown(f"### 🏃‍♂️ Streak: {st.session_state.streak} Days")
week_num = st.sidebar.number_input("Training Week", min_value=1, value=1)
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
target_mult = 1.0 if difficulty == "Standard" else 1.5 if difficulty == "Elite" else 2.0

# --- 5. Main Workout Hub ---
st.title("Performance Tracker")
drills = get_workout_template()

for i, item in enumerate(drills):
    drill_key = f"drill_{i}"
    if drill_key not in st.session_state.set_counters: st.session_state.set_counters[drill_key] = 0

    reps_per_set = int((item['base_reps'] + ((week_num - 1) * item['inc'])) * target_mult)
    
    st.markdown(f'<p class="drill-header">{item["ex"]}</p>', unsafe_allow_html=True)
    current_set = st.session_state.set_counters[drill_key]
    st.markdown(f'<div class="set-badge">Set {current_set} of {item["sets"]} Complete</div>', unsafe_allow_html=True)
    
    # 1. Main Controls (Always Visible)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Target", f"{reps_per_set} {item['unit']}")
        if st.button(f"Mark Set Done", key=f"done_{i}"):
            if st.session_state.set_counters[drill_key] < item['sets']:
                st.session_state.set_counters[drill_key] += 1
                st.rerun()
    with c2:
        if st.button(f"Start 30s Rest", key=f"timer_{i}"):
            ph = st.empty()
            for t in range(30, -1, -1):
                ph.markdown(f'<p class="timer-text">{t:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state.set_counters[drill_key] = min(st.session_state.set_counters[drill_key] + 1, item['sets'])
            st.rerun()
    with c3:
        val = st.number_input(f"Logged {item['unit']}", key=f"val_{i}", min_value=0)
        rpe = st.select_slider("RPE", options=range(1,11), value=7, key=f"rpe_{i}")
        st.session_state.session_history[item['ex']] = {"val": val, "rpe": rpe}

    # 2. Toggleable Video & Eval Section
    with st.expander("🎥 View Form Analysis & Coach's Evaluation"):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("**Pro Demonstration**")
            st.video(item['vid'])
        with col_v2:
            st.markdown("**Your Form**")
            uploaded_video = st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"up_{i}")
            if uploaded_video: st.video(uploaded_video)
            else: st.info("Tap to select video from gallery.")

        st.markdown('<div class="coach-eval">', unsafe_allow_html=True)
        st.markdown("**Coach's Checklist**")
        q1 = st.checkbox("Balance & Posture", key=f"q1_{i}")
        q2 = st.checkbox("Game Intensity", key=f"q2_{i}")
        notes = st.text_input("Quick Adjustment:", key=f"note_{i}", placeholder="What to fix next set...")
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

if st.button("Complete Workout"):
    update_streak()
    st.balloons()
    st.success(f"Session Saved! Streak: {st.session_state.streak} Days.")
