import streamlit as st
import pandas as pd
import time
import re
import os
from datetime import datetime
import plotly.express as px

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
        margin-top: 20px;
        letter-spacing: 1px;
        font-family: 'Arial Black', sans-serif;
        border-left: 5px solid #FFD700;
        padding-left: 15px;
    }
    
    /* Massive Timer Display */
    .timer-text {
        font-size: 60px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .stButton>button { 
        background-color: #FFD700; 
        color: #013220; 
        border-radius: 8px; 
        font-weight: bold; 
        border: 2px solid #DAA520; 
        width: 100%; 
        height: 60px;
        font-size: 20px;
    }
    
    .stMetric { 
        background-color: #004d26; 
        padding: 15px; 
        border-radius: 10px; 
        border: 3px solid #FFD700; 
    }
    
    h1 { color: #FFD700 !important; font-size: 48px !important; text-align: center; border-bottom: 4px solid #FFD700; padding-bottom: 15px; }
    
    .stExpander { 
        border: 2px solid #FFD700 !important; 
        background-color: #01411c !important; 
    }
    </style>
    """, unsafe_allow_html=True)

def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "Perfects (Form Shooting)", "base": 10, "inc": 2, "unit": "swishes", "rest": "1m", "vid": "https://youtu.be/akSJjN8UIj0"},
            {"ex": "Mikan Drill", "base": 20, "inc": 4, "unit": "makes", "rest": "1m", "vid": "https://youtu.be/akSJjN8UIj0"},
            {"ex": "Figure 8 Dribbling", "base": 60, "inc": 10, "unit": "seconds", "rest": "1m", "vid": "—"},
            {"ex": "Zig-Zag Defensive Slides", "base": 4, "inc": 1, "unit": "trips", "rest": "2m", "vid": "—"},
            {"ex": "Kyrie Finishing Drill", "base": 12, "inc": 3, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "Plus/Minus 3pt Shooting", "base": 2, "inc": 0.5, "unit": "minutes", "rest": "2m", "vid": "—"},
            {"ex": "Free Throw Pressure", "base": 10, "inc": 2, "unit": "makes", "rest": "1m", "vid": "—"},
            {"ex": "17s Conditioning", "base": 2, "inc": 1, "unit": "sprints", "rest": "3m", "vid": "—"}
        ],
        "Track": [
            {"ex": "Ankle Dribbles", "base": 20, "inc": 5, "unit": "meters", "rest": "30s", "vid": "—"},
            {"ex": "A-Skips", "base": 30, "inc": 5, "unit": "meters", "rest": "45s", "vid": "—"},
            {"ex": "Block Starts", "base": 4, "inc": 1, "unit": "reps", "rest": "4m", "vid": "—"},
            {"ex": "Wicket Runs", "base": 5, "inc": 1, "unit": "reps", "rest": "3m", "vid": "—"},
            {"ex": "Flying 30s", "base": 3, "inc": 1, "unit": "reps", "rest": "5m", "vid": "—"},
            {"ex": "Speed Skips (Height)", "base": 30, "inc": 5, "unit": "meters", "rest": "60s", "vid": "—"},
            {"ex": "Sled Pushes", "base": 4, "inc": 1, "unit": "reps", "rest": "3m", "vid": "—"},
            {"ex": "Tempo Strides", "base": 2, "inc": 1, "unit": "reps", "rest": "90s", "vid": "—"}
        ],
        "Softball": [
            {"ex": "Tee Work (Contact)", "base": 20, "inc": 5, "unit": "swings", "rest": "1m", "vid": "—"},
            {"ex": "Front Toss (Power)", "base": 15, "inc": 5, "unit": "swings", "rest": "2m", "vid": "—"},
            {"ex": "Infield Charging", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "Backhand Drills", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "Baserunning (Home to 1st)", "base": 5, "inc": 1, "unit": "sprints", "rest": "2m", "vid": "—"},
            {"ex": "Long Toss", "base": 10, "inc": 2, "unit": "minutes", "rest": "2m", "vid": "—"},
            {"ex": "Agility Ladder", "base": 4, "inc": 1, "unit": "sets", "rest": "1m", "vid": "—"},
            {"ex": "Pop-up Tracking", "base": 8, "inc": 2, "unit": "reps", "rest": "1m", "vid": "—"}
        ],
        "General Workout": [
            {"ex": "Goblet Squats", "base": 8, "inc": 2, "unit": "reps", "rest": "2m", "vid": "—"},
            {"ex": "Pushups", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "Dumbbell Rows", "base": 8, "inc": 2, "unit": "reps/arm", "rest": "90s", "vid": "—"},
            {"ex": "Walking Lunges", "base": 10, "inc": 2, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "Plank Hold", "base": 30, "inc": 10, "unit": "seconds", "rest": "60s", "vid": "—"},
            {"ex": "Med Ball Slams", "base": 10, "inc": 2, "unit": "reps", "rest": "60s", "vid": "—"},
            {"ex": "Box Jumps", "base": 5, "inc": 1, "unit": "reps", "rest": "2m", "vid": "—"},
            {"ex": "Mountain Climbers", "base": 30, "inc": 10, "unit": "seconds", "rest": "60s", "vid": "—"}
        ]
    }
    return workouts.get(sport, [])

st.sidebar.header("🥇 ATHLETE PROFILE")
sport = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
env = st.sidebar.radio("Setting", ["Indoor", "Outdoor", "Combination"])
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
session_num = st.sidebar.number_input("Session Number", min_value=1, value=1)

st.header("📋 Readiness Check")
r_col1, r_col2, r_col3 = st.columns(3)
with r_col1: sleep = st.slider("Sleep Quality (1-5)", 1, 5, 4)
with r_col2: soreness = st.slider("Soreness (1=Fresh, 5=Sore)", 1, 5, 2)
with r_col3: energy = st.slider("Energy (1-5)", 1, 5, 4)

st.divider()
st.header(f"🔥 {sport} | Session {session_num}")
drills = get_workout_template(sport)

for i, item in enumerate(drills):
    target_val = item['base'] + ((week_num - 1) * item['inc'])
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("DRILL DETAILS", expanded=True):
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
                st.success("GO!")
        with c3:
            st.text_input("Log Result", key=f"log_{i}")
            st.select_slider("Intensity (RPE)", options=range(1, 11), value=7, key=f"rpe_{i}")

st.divider()
if st.button("💾 SAVE SESSION DATA"):
    st.balloons()
    st.success(f"Session {session_num} Successfully Logged!")
