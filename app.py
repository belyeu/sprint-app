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

# --- 2. SIDEBAR (RESTORED FEATURES) ---
with st.sidebar:
    # Restored Date/Time
    st.markdown(f"""
    <div style="background-color:#3B82F6; padding:15px; border-radius:10px; text-align:center; margin-bottom:20px;">
        <h2 style="color:white; margin:0;">{get_now_est().strftime('%I:%M %p')}</h2>
        <p style="color:white; margin:0; opacity:0.8;">{get_now_est().strftime('%A, %b %d')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    location = st.selectbox("Location", ["Gym", "Softball Field", "Batting Cages", "Track", "Weight Room"])
    sport_choice = st.selectbox("Sport Database", ["Basketball", "Softball", "Track", "General"])
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = None

# Custom CSS
st.markdown("""
<style>
.drill-header {
    font-size: 20px !important; font-weight: 800 !important;
    color: #3B82F6 !important; background-color: #1E293B; 
    border-left: 8px solid #3B82F6; padding: 12px; margin-top: 20px; border-radius: 4px;
}
.stat-box {
    background-color: #1E293B; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE ---
def get_vault():
    return {
        "Basketball": [
            {"ex": "Iverson Cross", "desc": "Wide deceptive step-across.", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "25s per set", "focus": ["Width", "Deception"]},
            {"ex": "Shammgod", "desc": "Push out R, pull back L.", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "15s per set", "focus": ["Extension", "Speed"]},
            {"ex": "Pocket Pulls", "desc": "Pull ball to hip pocket.", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s per set", "focus": ["Security", "Wrist Snap"]},
            {"ex": "Trae Young Pullback", "desc": "Lunge forward and snap back.", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "20s per set", "focus": ["Deceleration", "Balance"]}
            # ... additional basketball items would go here
        ],
        "Softball": [
            {"ex": "Shuffle Step Throw", "desc": "Instep to instep throw.", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "45s per set", "focus": ["Accuracy", "Footwork"]},
            {"ex": "Power Step", "desc": "Instep to ball; move around.", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "40s per set", "focus": ["Wrap Around Tag"]},
            {"ex": "Jam Step Backhand", "desc": "Glove foot steps with ball.", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "30s per set", "focus": ["Drop And Up"]}
            # ... additional softball items would go here
        ],
        "Track": [
            {"ex": "Flying 30s", "desc": "Pure Top-End Speed.", "sets": 4, "base": 30, "unit": "m", "rest": 180, "time_goal": "Under 4.0s", "focus": ["Relaxed Upper Body"]},
            {"ex": "Wicket Flys", "desc": "Max Velocity Maintenance.", "sets": 4, "base": 40, "unit": "m", "rest": 120, "time_goal": "Under 5.2s", "focus": ["Frequency"]}
        ],
        "General": [
            {"ex": "Power Clean", "desc": "Rate of Force Development.", "sets": 5, "base": 3, "unit": "reps", "rest": 120, "time_goal": "Explosive", "focus": ["Full Extension"]},
            {"ex": "Bulgarian Split Squat", "desc": "Unilateral Strength.", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "time_goal": "Controlled", "focus": ["Depth"]}
        ]
    }

# --- 4. SESSION HANDLING ---
vault = get_vault()
count_needed = 12 if sport_choice in ["Basketball", "Softball"] else 8

if st.session_state.active_sport != sport_choice or st.session_state.current_session is None:
    available_drills = vault.get(sport_choice, [])
    st.session_state.current_session = random.sample(available_drills, min(len(available_drills), count_needed))
    st.session_state.active_sport = sport_choice

# --- 5. MAIN UI ---
st.title(f"🔥 {difficulty} {sport_choice} Session")

mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

for i, drill in enumerate(st.session_state.current_session):
    st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        # Rep/Set Goals
        target_reps = int(drill['base'] * mult)
        st.markdown(f"**Target:** {drill['sets']} Sets x {target_reps} {drill['unit']}")
        st.markdown(f"⏱️ **Timing Goal:** `{drill['time_goal']}`")
        st.write(f"_{drill['desc']}_")
        
        # Completed Set Tracker
        st.markdown("**Mark Completed Sets:**")
        set_cols = st.columns(drill['sets'])
        for s in range(drill['sets']):
            set_cols[s].checkbox(f"S{s+1}", key=f"set_{i}_{s}")
            
    with col2:
        # Rest and Timing Goals
        st.markdown(f"⌛ **Recommended Rest: {drill['rest']}s**")
        if st.button(f"START REST TIMER", key=f"btn_{i}"):
            timer_box = st.empty()
            for s in range(drill['rest'], -1, -1):
                timer_box.metric("Rest Remaining", f"{s}s")
                time.sleep(1)
            timer_box.empty()
            st.success("Set Recovery Complete!")
        
        st.markdown("🎯 **Coach's Eval**")
        for f in drill["focus"]:
            st.checkbox(f, key=f"eval_{i}_{f}")

    with col3:
        st.markdown("🎥 **Action**")
        st.button("Watch Demo", key=f"demo_{i}")
        st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"up_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "loc": location})
    st.balloons()
    st.success("Session saved to Performance History!")
