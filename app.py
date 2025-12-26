import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime

# --- Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #013220; color: #ffffff; }
    .drill-header {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: #FFD700 !important;
        text-transform: uppercase;
        margin-bottom: 5px;
        margin-top: 25px;
        font-family: 'Arial Black', sans-serif;
        border-left: 8px solid #FFD700;
        padding-left: 20px;
    }
    .timer-text {
        font-size: 85px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        background: #004d26;
        border-radius: 12px;
        border: 4px solid #FFD700;
        padding: 15px;
    }
    .stButton>button { 
        background-color: #FFD700; 
        color: #013220; 
        border-radius: 10px; 
        font-weight: bold; 
        border: 2px solid #DAA520; 
        width: 100%; 
        height: 60px;
        font-size: 22px;
    }
    .stMetric { 
        background-color: #004d26; 
        padding: 20px; 
        border-radius: 12px; 
        border: 3px solid #FFD700; 
    }
    h1 { color: #FFD700 !important; font-size: 52px !important; text-align: center; border-bottom: 5px solid #FFD700; padding-bottom: 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES (STATIONARY)", "base": 60, "inc": 15, "unit": "seconds", "rest": 30, "type": "cond"},
            {"ex": "FIGURE 8 SERIES (WRAPS)", "base": 90, "inc": 20, "unit": "seconds", "rest": 30, "type": "cond"},
            {"ex": "STATIONARY CROSSOVER SERIES", "base": 100, "inc": 25, "unit": "reps", "rest": 45, "type": "power"},
            {"ex": "MOVING CROSSOVER SERIES", "base": 10, "inc": 2, "unit": "trips", "rest": 60, "type": "power"},
            {"ex": "LATERAL DEFENSIVE SLIDE SERIES", "base": 8, "inc": 2, "unit": "trips", "rest": 90, "type": "power"},
            {"ex": "FLOAT DRIBBLE SERIES (HANG)", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power"},
            {"ex": "SLIDE TO FLOAT TRANSITION", "base": 30, "inc": 5, "unit": "reps", "rest": 60, "type": "power"},
            {"ex": "MIKAN SERIES (TOUCH)", "base": 50, "inc": 10, "unit": "makes", "rest": 60, "type": "power"}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLE SERIES", "base": 40, "inc": 10, "unit": "meters", "rest": 30, "type": "cond"},
            {"ex": "A-SERIES MARCH (POSTURE)", "base": 50, "inc": 10, "unit": "meters", "rest": 45, "type": "cond"},
            {"ex": "A-SERIES SKIP (RHYTHM)", "base": 60, "inc": 10, "unit": "meters", "rest": 60, "type": "power"},
            {"ex": "WICKET RHYTHM SERIES", "base": 12, "inc": 2, "unit": "reps", "rest": 180, "type": "power"},
            {"ex": "BLOCK START EXPLOSION SERIES", "base": 8, "inc": 2, "unit": "reps", "rest": 240, "type": "power"},
            {"ex": "MAX VELOCITY FLY SERIES", "base": 6, "inc": 1, "unit": "reps", "rest": 300, "type": "power"},
            {"ex": "POWER SKIP SERIES (HEIGHT)", "base": 50, "inc": 10, "unit": "meters", "rest": 60, "type": "power"},
            {"ex": "SPEED ENDURANCE SERIES", "base": 5, "inc": 1, "unit": "reps", "rest": 120, "type": "cond"}
        ],
        "Softball": [
            {"ex": "TEE SERIES (BALANCE/RHYTHM)", "base": 50, "inc": 15, "unit": "swings", "rest": 60, "type": "power"},
            {"ex": "FRONT TOSS POWER SERIES", "base": 40, "inc": 10, "unit": "swings", "rest": 120, "type": "power"},
            {"ex": "INFIELD GLOVE WORK (KNEES)", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power"},
            {"ex": "INFIELD CHARGING SERIES", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power"},
            {"ex": "BACKHAND/FOREHAND SERIES", "base": 30, "inc": 5, "unit": "reps", "rest": 90, "type": "power"},
            {"ex": "BASERUNNING SPRINT SERIES", "base": 12, "inc": 2, "unit": "sprints", "rest": 120, "type": "power"},
            {"ex": "LATERAL AGILITY SLIDE SERIES", "base": 10, "inc": 2, "unit": "sets", "rest": 60, "type": "cond"},
            {"ex": "FLY BALL TRACKING SERIES", "base": 20, "inc": 5, "unit": "reps", "rest": 60, "type": "cond"}
        ],
        "General Workout": [
            {"ex": "SQUAT PATTERN SERIES", "base": 15, "inc": 3, "unit": "reps", "rest": 120, "type": "power"},
            {"ex": "PUSHUP PROGRESSION SERIES", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power"},
            {"ex": "PULL/ROW SERIES", "base": 12, "inc": 2, "unit": "reps/arm", "rest": 90, "type": "power"},
            {"ex": "UNILATERAL LUNGE SERIES", "base": 15, "inc": 2, "unit": "reps", "rest": 90, "type": "power"},
            {"ex": "CORE ISOMETRIC SERIES", "base": 60, "inc": 15, "unit": "seconds", "rest": 60, "type": "cond"},
            {"ex": "BALLISTIC SLAM SERIES", "base": 20, "inc": 5, "unit": "reps", "rest": 60, "type": "power"},
            {"ex": "PLYOMETRIC JUMP SERIES", "base": 12, "inc": 2, "unit": "reps", "rest": 120, "type": "power"},
            {"ex": "DYNAMIC CONDITIONING SERIES", "base": 60, "inc": 15, "unit": "seconds", "rest": 60, "type": "cond"}
        ]
    }
    return workouts.get(sport, [])

# --- Sidebar ---
st.sidebar.header("🥇 ATHLETE PROFILE")
sport = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
session_num = st.sidebar.number_input("Session Number", min_value=1, value=1)

# Logic Multipliers
target_mult = 1.0 if difficulty == "Standard" else 1.5 if difficulty == "Elite" else 2.0
# Rest Multiplier: Pro athletes take SHORTER rest for conditioning, LONGER for max power
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- Workout UI ---
st.header(f"🔥 {sport} | Level: {difficulty}")
drills = get_workout_template(sport)

for i, item in enumerate(drills):
    # Calculate Dynamic Target
    target_val = int((item['base'] + ((week_num - 1) * item['inc'])) * target_mult)
    
    # Calculate Dynamic Rest
    if item['type'] == 'power':
        # More rest for elite power production
        final_rest = int(item['rest'] * rest_mult)
    else:
        # Less rest for elite conditioning (inverse the multiplier)
        final_rest = int(item['rest'] / rest_mult)
        
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("DRILL DETAILS & LOGGING", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Target", f"{target_val} {item['unit']}")
        with c2:
            mins, secs = divmod(final_rest, 60)
            rest_display = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
            st.write(f"**Optimal Rest:** {rest_display}")
            
            if st.button(f"⏱️ Start Timer", key=f"timer_{i}"):
                ph = st.empty()
                for t in range(final_rest, -1, -1):
                    m, s = divmod(t, 60)
                    ph.markdown(f'<p class="timer-text">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
                    time.sleep(1)
                st.success("NEXT SET!")
        with c3:
            st.text_input("Log Result", key=f"log_{i}")
            st.select_slider("RPE", options=range(1, 11), value=8, key=f"rpe_{i}")

if st.button("💾 SAVE SESSION DATA"):
    st.balloons()
    st.success("Session Saved!")
