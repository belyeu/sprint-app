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
    
    /* Massive Drill Headers */
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
    
    /* Massive Timer Display */
    .timer-text {
        font-size: 75px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        background: #004d26;
        border-radius: 12px;
        border: 3px solid #FFD700;
        padding: 10px;
        margin: 10px 0;
    }
    
    .stButton>button { 
        background-color: #FFD700; 
        color: #013220; 
        border-radius: 10px; 
        font-weight: bold; 
        border: 2px solid #DAA520; 
        width: 100%; 
        height: 60px;
        font-size: 20px;
    }
    
    .stMetric { 
        background-color: #004d26; 
        padding: 15px; 
        border-radius: 12px; 
        border: 3px solid #FFD700; 
    }
    
    h1 { color: #FFD700 !important; font-size: 52px !important; text-align: center; border-bottom: 5px solid #FFD700; padding-bottom: 15px; text-transform: uppercase; }
    
    .stExpander { 
        border: 2px solid #FFD700 !important; 
        background-color: #01411c !important; 
    }
    </style>
    """, unsafe_allow_html=True)

def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES (STATIONARY)", "base": 30, "inc": 10, "unit": "seconds", "rest": "30s", "vid": "—"},
            {"ex": "FIGURE 8 SERIES (WRAPS)", "base": 45, "inc": 15, "unit": "seconds", "rest": "30s", "vid": "—"},
            {"ex": "STATIONARY CROSSOVER SERIES", "base": 50, "inc": 10, "unit": "reps", "rest": "45s", "vid": "https://wattsbasketball.com/blog/crossover-dribble-in-basketball"},
            {"ex": "MOVING CROSSOVER SERIES", "base": 4, "inc": 1, "unit": "trips", "rest": "1m", "vid": "https://www.online-basketball-drills.com/in-out-with-crossover-drill"},
            {"ex": "LATERAL DEFENSIVE SLIDE SERIES", "base": 4, "inc": 1, "unit": "trips", "rest": "90s", "vid": "—"},
            {"ex": "FLOAT DRIBBLE SERIES (HANG)", "base": 20, "inc": 5, "unit": "reps", "rest": "1m", "vid": "https://www.youtube.com/watch?v=G-ylr5AQExw"},
            {"ex": "SLIDE TO FLOAT TRANSITION", "base": 10, "inc": 2, "unit": "reps", "rest": "1m", "vid": "—"},
            {"ex": "MIKAN SERIES (TOUCH)", "base": 20, "inc": 5, "unit": "makes", "rest": "1m", "vid": "—"}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLE SERIES", "base": 20, "inc": 5, "unit": "meters", "rest": "30s", "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw"},
            {"ex": "A-SERIES MARCH (POSTURE)", "base": 30, "inc": 5, "unit": "meters", "rest": "45s", "vid": "https://marathonhandbook.com/a-skips/"},
            {"ex": "A-SERIES SKIP (RHYTHM)", "base": 30, "inc": 5, "unit": "meters", "rest": "1m", "vid": "https://dlakecreates.com/how-to-do-askips-drill-for-distance-runners/"},
            {"ex": "WICKET RHYTHM SERIES", "base": 6, "inc": 1, "unit": "reps", "rest": "3m", "vid": "—"},
            {"ex": "BLOCK START EXPLOSION SERIES", "base": 4, "inc": 1, "unit": "reps", "rest": "4m", "vid": "—"},
            {"ex": "MAX VELOCITY FLY SERIES", "base": 3, "inc": 1, "unit": "reps", "rest": "5m", "vid": "—"},
            {"ex": "POWER SKIP SERIES (HEIGHT)", "base": 30, "inc": 5, "unit": "meters", "rest": "1m", "vid": "—"},
            {"ex": "SPEED ENDURANCE SERIES", "base": 2, "inc": 1, "unit": "reps", "rest": "2m", "vid": "—"}
        ],
        "Softball": [
            {"ex": "TEE SERIES (BALANCE/RHYTHM)", "base": 20, "inc": 5, "unit": "swings", "rest": "1m", "vid": "https://probaseballinsider.com/pregame-1-batting-drills/"},
            {"ex": "FRONT TOSS POWER SERIES", "base": 15, "inc": 5, "unit": "swings", "rest": "2m", "vid": "—"},
            {"ex": "INFIELD GLOVE WORK (KNEES)", "base": 15, "inc": 5, "unit": "reps", "rest": "1m", "vid": "https://www.littleleague.org/university/articles/infield-drill-progression/"},
            {"ex": "INFIELD CHARGING SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "BACKHAND/FOREHAND SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "BASERUNNING SPRINT SERIES", "base": 5, "inc": 1, "unit": "sprints", "rest": "2m", "vid": "—"},
            {"ex": "LATERAL AGILITY SLIDE SERIES", "base": 4, "inc": 1, "unit": "sets", "rest": "1m", "vid": "—"},
            {"ex": "FLY BALL TRACKING SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "1m", "vid": "—"}
        ],
        "General Workout": [
            {"ex": "SQUAT PATTERN SERIES", "base": 8, "inc": 2, "unit": "reps", "rest": "2m", "vid": "—"},
            {"ex": "PUSHUP PROGRESSION SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "PULL/ROW SERIES", "base": 8, "inc": 2, "unit": "reps/arm", "rest": "90s", "vid": "—"},
            {"ex": "UNILATERAL LUNGE SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "CORE ISOMETRIC SERIES", "base": 30, "inc": 10, "unit": "seconds", "rest": "60s", "vid": "—"},
            {"ex": "BALLISTIC SLAM SERIES", "base": 10, "inc": 2, "unit": "reps", "rest": "60s", "vid": "—"},
            {"ex": "PLYOMETRIC JUMP SERIES", "base": 5, "inc": 1, "unit": "reps", "rest": "2m", "vid": "—"},
            {"ex": "DYNAMIC CONDITIONING SERIES", "base": 30, "inc": 10, "unit": "seconds", "rest": "60s", "vid": "—"}
        ]
    }
    return workouts.get(sport, [])

# --- Sidebar ---
st.sidebar.header("🥇 ATHLETE PROFILE")
sport = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
session_num = st.sidebar.number_input("Session Number", min_value=1, value=1)

# --- 1. Readiness Check ---
st.header("📋 Readiness Check")
r_col1, r_col2, r_col3 = st.columns(3)
with r_col1: sleep = st.slider("Sleep Quality (1-5)", 1, 5, 4)
with r_col2: soreness = st.slider("Soreness (1=Fresh, 5=Sore)", 1, 5, 2)
with r_col3: energy = st.slider("Energy (1-5)", 1, 5, 4)

# --- 2. Dynamic Workout ---
st.divider()
st.header(f"🔥 {sport} | Session {session_num}")
drills = get_workout_template(sport)

for i, item in enumerate(drills):
    target_val = item['base'] + ((week_num - 1) * item['inc'])
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("DRILL DETAILS & LOGGING", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Target", f"{target_val} {item['unit']}")
            if item['vid'] != "—": st.link_button("📺 Watch Form", item['vid'])
        with c2:
            st.write(f"**Rest:** {item['rest']}")
            if st.button(f"⏱️ Start Timer", key=f"timer_{i}"):
                time_match = re.search(r'\d+', item['rest'])
                seconds = int(time_match.group()) * (60 if 'm' in item['rest'] else 1)
                ph = st.empty()
                for t in range(seconds, -1, -1):
                    mins, secs = divmod(t, 60)
                    ph.markdown(f'<p class="timer-text">{mins:02d}:{secs:02d}</p>', unsafe_allow_html=True)
                    time.sleep(1)
                st.success("NEXT SET!")
        with c3:
            st.text_input("Log Result", key=f"log_{i}", placeholder="Actual score...")
            st.select_slider("Intensity (RPE)", options=range(1, 11), value=7, key=f"rpe_{i}")

# --- 3. Final Save ---
st.divider()
if st.button("💾 SAVE SESSION DATA"):
    st.balloons()
    st.success(f"Session {session_num} Successfully Logged!")
