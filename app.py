import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, date, timedelta

# --- 1. Refined Modern Athletic Theme ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #F8FAFC; color: #1E293B; }
    
    /* DRILL NAME - UPDATED FOR HIGH VISIBILITY */
    .drill-header {
        font-size: 30px !important; 
        font-weight: 800 !important; 
        color: #0F172A !important; /* Deep Navy - very visible on white */
        margin-top: 30px; 
        margin-bottom: 10px;
        background-color: #FFFFFF; /* White background for the text area */
        border-left: 8px solid #3B82F6; /* Bright Blue accent */
        padding: 12px 20px;
        border-radius: 4px 12px 12px 4px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Timer Display */
    .timer-text {
        font-size: 65px !important; font-weight: 700 !important; color: #3B82F6 !important;
        text-align: center; background: #EFF6FF; border-radius: 16px; padding: 15px;
        border: 2px solid #DBEAFE;
    }
    
    /* Sidebar Streak Card */
    .streak-card {
        background: white; color: #1E293B; padding: 20px; border-radius: 12px; 
        text-align: center; font-weight: 700; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

    /* Buttons */
    .stButton>button { 
        background-color: #3B82F6; color: white; border-radius: 10px; 
        font-weight: 700; height: 55px; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State Logic ---
if 'streak' not in st.session_state: st.session_state.streak = 1
if 'set_counters' not in st.session_state: st.session_state.set_counters = {}

def get_workout_template():
    return [
        {"ex": "Pound Series", "base": 30, "sets": 4, "bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
        {"ex": "Mikan Series", "base": 25, "sets": 4, "bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"},
        {"ex": "Stationary Crossover", "base": 50, "sets": 4, "bench": 400, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E"}
    ]

# --- 3. Sidebar Analytics ---
st.sidebar.markdown(f"""
    <div class="streak-card">
        <p style="margin:0; font-size: 12px; color: #64748B;">DAILY STREAK</p>
        <p style="margin:0; font-size: 32px; color: #3B82F6;">{st.session_state.streak} Days 🔥</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. Main Workout View ---
st.title("Performance Tracker")
drills = get_workout_template()

for i, item in enumerate(drills):
    drill_key = f"drill_{i}"
    if drill_key not in st.session_state.set_counters: st.session_state.set_counters[drill_key] = 0
    
    # Drill Name Display
    st.markdown(f'<p class="drill-header">{item["ex"]}</p>', unsafe_allow_html=True)
    
    current_set = st.session_state.set_counters[drill_key]
    st.write(f"**Progress:** Set {current_set} of {item['sets']}")

    # Main Controls
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Goal", f"{item['base']} Reps")
        if st.button(f"Mark Set Done", key=f"done_{i}"):
            st.session_state.set_counters[drill_key] = min(st.session_state.set_counters[drill_key]+1, item['sets'])
            st.rerun()
    with c2:
        if st.button(f"Start Rest", key=f"timer_{i}"):
            ph = st.empty()
            for t in range(30, -1, -1):
                ph.markdown(f'<p class="timer-text">{t:02d}s</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.rerun()
    with c3:
        st.number_input("Log Reps", key=f"log_{i}", min_value=0)
        st.select_slider("Intensity", options=range(1,11), value=7, key=f"rpe_{i}")

    # Toggle for Video/Eval
    with st.expander("🎥 View Form & Evaluation"):
        v1, v2 = st.columns(2)
        with v1: st.video(item['vid'])
        with v2:
            up = st.file_uploader("Upload Gallery Clip", type=["mp4", "mov"], key=f"up_{i}")
            if up: st.video(up)

st.divider()
if st.button("Complete Workout"):
    st.balloons()
    st.success("Session saved!")
