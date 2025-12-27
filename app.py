import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, date, timedelta

# --- 1. Modern Athletic Theme ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; color: #1E293B; }
    .drill-header {
        font-size: 26px !important; font-weight: 800 !important; color: #0F172A !important;
        margin-top: 20px; border-left: 5px solid #3B82F6; padding-left: 15px;
    }
    .timer-text {
        font-size: 60px !important; font-weight: 700 !important; color: #3B82F6 !important;
        text-align: center; background: #EFF6FF; border-radius: 12px; padding: 10px;
    }
    .set-badge {
        background-color: #10B981; color: white; padding: 5px 12px;
        border-radius: 15px; font-weight: 600; font-size: 13px; display: inline-block;
    }
    .stButton>button { 
        background-color: #3B82F6; color: white; border-radius: 8px; font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State ---
if 'streak' not in st.session_state: st.session_state.streak = 5 # Dummy data
if 'set_counters' not in st.session_state: st.session_state.set_counters = {}
if 'history' not in st.session_state: 
    # Generating dummy history for the graph
    dates = [date.today() - timedelta(days=x) for x in range(7, 0, -1)]
    st.session_state.history = pd.DataFrame({
        'Day': dates,
        'Pound Series': [180, 200, 190, 210, 220, 230, 245],
        'Mikan Series': [80, 85, 90, 88, 95, 102, 110]
    }).set_index('Day')

# --- 3. Sidebar & Analytics ---
st.sidebar.title("📊 Athlete Analytics")
st.sidebar.markdown(f"**Current Streak:** {st.session_state.streak} Days 🔥")

with st.sidebar:
    st.markdown("### Weekly Progress")
    # Using built-in st.line_chart for clean analytics
    st.line_chart(st.session_state.history)

# --- 4. Main Workout Hub ---
st.title("Performance Tracker")
tabs = st.tabs(["Active Workout", "Drill Library"])

with tabs[0]:
    drills = [
        {"ex": "Pound Series", "base": 30, "sets": 4, "bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
        {"ex": "Mikan Series", "base": 25, "sets": 4, "bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"}
    ]

    for i, item in enumerate(drills):
        drill_key = f"drill_{i}"
        if drill_key not in st.session_state.set_counters: st.session_state.set_counters[drill_key] = 0
        
        st.markdown(f'<p class="drill-header">{item["ex"]}</p>', unsafe_allow_html=True)
        
        # Pro Benchmark Progress Bar
        current_val = st.session_state.get(f"val_{i}", 0)
        progress_pct = min(current_val / item['bench'], 1.0)
        st.write(f"Pro Benchmark: {int(progress_pct*100)}%")
        st.progress(progress_pct)

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Set", f"{st.session_state.set_counters[drill_key]} / {item['sets']}")
            if st.button("Set Done", key=f"d_{i}"):
                st.session_state.set_counters[drill_key] = min(st.session_state.set_counters[drill_key]+1, item['sets'])
                st.rerun()
        with c2:
            if st.button("Rest 30s", key=f"t_{i}"):
                ph = st.empty()
                for t in range(30, -1, -1):
                    ph.markdown(f'<p class="timer-text">{t:02d}</p>', unsafe_allow_html=True)
                    time.sleep(1)
                st.rerun()
        with c3:
            st.session_state[f"val_{i}"] = st.number_input("Total Reps", key=f"in_{i}", value=current_val)

        with st.expander("🎥 View Form & Evaluation"):
            col1, col2 = st.columns(2)
            with col1: st.video(item['vid'])
            with col2:
                uploaded = st.file_uploader("Upload Gallery Clip", type=["mp4", "mov"], key=f"up_{i}")
                if uploaded: st.video(uploaded)
            
            st.checkbox("Game Speed Effort?", key=f"q_{i}")
            st.text_input("Coach's Note:", key=f"n_{i}")

st.divider()
if st.button("Complete Workout"):
    st.balloons()
    st.success("Session saved to Athlete Analytics.")
