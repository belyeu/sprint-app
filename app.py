import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None
if 'active_sport' not in st.session_state: st.session_state.active_sport = ""

# --- 2. SIDEBAR ---
with st.sidebar:
    # Sidebar Date/Time Card
    st.markdown(f"""
    <div style="background-color:#1E293B; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#3B82F6; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#60A5FA; margin:0; font-weight:bold; letter-spacing:1px;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    location = st.selectbox("Location", ["Gym", "Softball Field", "Batting Cages", "Track", "Weight Room"])
    sport_choice = st.selectbox("Sport Database", ["Basketball", "Softball", "Track", "General"])
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = None

# --- 3. CUSTOM CSS (BLUE SIDEBAR TEXT & DARK MODE) ---
st.markdown(f"""
<style>
    /* Main App Background */
    .stApp {{ background-color: #0F172A !important; }}
    
    /* Sidebar Background matching App */
    [data-testid="stSidebar"] {{
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }}
    
    /* GLOBAL SIDEBAR TEXT TO BLUE */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] span {{
        color: #3B82F6 !important;
        font-weight: 600 !important;
    }}

    /* Main Area Styling */
    .drill-header {{
        font-size: 20px !important; font-weight: 800 !important;
        color: #3B82F6 !important; background-color: #1E293B; 
        border-left: 8px solid #3B82F6; padding: 12px; margin-top: 20px; border-radius: 4px;
    }}
    
    .metric-row {{
        background-color: #1E293B; padding: 12px; border-radius: 8px; margin: 8px 0; border: 1px solid #334155;
        color: #FFFFFF;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. DATABASE (REPS, SETS, TIME GOALS) ---
def get_vault():
    return {
        "Basketball": [
            {"ex": "Iverson Cross", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Wide deceptive step-across.", "focus": ["Width", "Low Hips"]},
            {"ex": "Shammgod", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "15s", "desc": "Push out R, pull back L.", "focus": ["Extension", "Speed"]},
            {"ex": "Pocket Pulls", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Pull ball to hip pocket.", "focus": ["Security", "Wrist Snap"]},
            {"ex": "Trae Young Pullback", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "18s", "desc": "Lunge forward and snap back.", "focus": ["Deceleration", "Balance"]}
        ],
        "Softball": [
            {"ex": "Shuffle Step Throw", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "40s", "desc": "Instep to instep throw.", "focus": ["Over Right Shoulder Tag"]},
            {"ex": "Power Step", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "35s", "desc": "Instep to ball; move around.", "focus": ["Wrap Around Tag"]}
        ],
        "Track": [
            {"ex": "Flying 30s", "sets": 4, "base": 30, "unit": "m", "rest": 180, "time_goal": "4.0s", "desc": "Pure Top-End Speed.", "focus": ["Relaxed Face"]},
            {"ex": "Wicket Flys", "sets": 4, "base": 40, "unit": "m", "rest": 120, "time_goal": "5.5s", "desc": "Max Velocity Maintenance.", "focus": ["Frequency"]}
        ],
        "General": [
            {"ex": "Power Clean", "sets": 5, "base": 3, "unit": "reps", "rest": 120, "time_goal": "Explosive", "desc": "Rate of Force Development.", "focus": ["Extension"]},
            {"ex": "Nordic Curls", "sets": 3, "base": 6, "unit": "reps", "rest": 90, "time_goal": "30s", "desc": "Eccentric Hamstring Safety.", "focus": ["Slow Descent"]}
        ]
    }

# --- 5. SESSION LOGIC ---
vault = get_vault()
count = 12 if sport_choice in ["Basketball", "Softball"] else 8

if st.session_state.active_sport != sport_choice or st.session_state.current_session is None:
    available = vault.get(sport_choice, [])
    st.session_state.current_session = random.sample(available, min(len(available), count))
    st.session_state.active_sport = sport_choice

# --- 6. MAIN UI ---
st.title(f"🔥 {difficulty} {sport_choice} Session")
mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

for i, drill in enumerate(st.session_state.current_session):
    st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-row">
            <span style="color:#60A5FA">Sets:</span> {drill['sets']} | 
            <span style="color:#60A5FA">Target:</span> {int(drill['base'] * mult)} {drill['unit']} | 
            <span style="color:#60A5FA">Goal:</span> {drill['time_goal']}
        </div>
        """, unsafe_allow_html=True)
        st.write(f"_{drill['desc']}_")
        
        st.markdown("**Mark Sets Completed:**")
        set_cols = st.columns(drill['sets'])
        for s in range(drill['sets']):
            set_cols[s].checkbox(f"S{s+1}", key=f"s_{i}_{s}")
            
    with col2:
        st.markdown(f"⏱️ **Recommended Rest: {drill['rest']}s**")
        if st.button(f"START TIMER", key=f"t_{i}"):
            ph = st.empty()
            for t in range(drill['rest'], -1, -1):
                ph.metric("Recovery", f"{t}s")
                time.sleep(1)
            ph.empty()
            st.success("Recovery Done!")
        
        st.markdown("🎯 **Coach's Eval**")
        for f in drill["focus"]:
            st.checkbox(f, key=f"f_{i}_{f}")

    with col3:
        st.markdown("🎥 **Evidence**")
        st.button("Demo", key=f"d_{i}")
        st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"u_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "loc": location})
    st.balloons()
    st.success("Session saved!")
