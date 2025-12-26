import streamlit as st
import pandas as pd
import time
import re
import os
from datetime import datetime
import plotly.express as px

# --- Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Green and Gold Varsity Styling
st.markdown("""
    <style>
    .main { background-color: #013220; color: #ffffff; }
    .stButton>button { background-color: #FFD700; color: #013220; border-radius: 8px; font-weight: bold; border: 2px solid #DAA520; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #DAA520; color: #ffffff; }
    .stMetric { background-color: #004d26; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .stExpander { border: 1px solid #FFD700 !important; background-color: #01411c !important; color: white !important; }
    .stSlider label { color: #FFD700 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Sport-Specific Data with Progressive Logic ---
def get_workout_template(sport):
    # base = Week 1 reps, inc = how many to add each week
    workouts = {
        "Basketball": [
            {"ex": "Mikan Drill (Finishing)", "base": 20, "inc": 5, "unit": "makes", "rest": "1m", "vid": "https://youtu.be/akSJjN8UIj0"},
            {"ex": "Perfects (Form Shooting)", "base": 10, "inc": 3, "unit": "swishes", "rest": "1m", "vid": "https://www.basketballforcoaches.com/basketball-drills-for-guards/"},
            {"ex": "Zig-Zag Defensive Slides", "base": 4, "inc": 1, "unit": "full court trips", "rest": "2m", "vid": "https://www.basketballforcoaches.com/basketball-drills-and-games-for-kids/"},
            {"ex": "Plus/Minus 3-Point Shooting", "base": 2, "inc": 0.5, "unit": "minutes", "rest": "2m", "vid": "—"},
            {"ex": "Figure 8 Dribbling", "base": 60, "inc": 15, "unit": "seconds", "rest": "1m", "vid": "—"},
            {"ex": "Kyrie Finishing Drill", "base": 15, "inc": 5, "unit": "reps", "rest": "90s", "vid": "—"}
        ],
        "Track": [
            {"ex": "Block Starts", "base": 4, "inc": 1, "unit": "reps", "rest": "4m", "vid": "https://youtu.be/1eX7v7S7eP0"},
            {"ex": "Wicket Runs", "base": 4, "inc": 2, "unit": "reps", "rest": "3m", "vid": "https://youtu.be/lS69U9Zp4rI"},
            {"ex": "Flying 30s", "base": 3, "inc": 1, "unit": "reps", "rest": "5m", "vid": "—"}
        ],
        "Softball": [
            {"ex": "Front Toss (Batting)", "base": 20, "inc": 10, "unit": "swings", "rest": "2m", "vid": "—"},
            {"ex": "Infield Charging Drills", "base": 12, "inc": 3, "unit": "reps", "rest": "90s", "vid": "—"},
            {"ex": "60ft Baserunning Sprints", "base": 5, "inc": 1, "unit": "reps", "rest": "2m", "vid": "—"}
        ],
        "General Workout": [
            {"ex": "Bulgarian Split Squats", "base": 6, "inc": 2, "unit": "reps/leg", "rest": "2m", "vid": "—"},
            {"ex": "Med Ball Slams", "base": 10, "inc": 2, "unit": "reps", "rest": "60s", "vid": "—"}
        ]
    }
    return workouts.get(sport, [])

# --- Sidebar Configuration ---
st.sidebar.header("🥇 ATHLETE PROFILE")
sport = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
env = st.sidebar.radio("Setting", ["Indoor", "Outdoor", "Combination"])
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
session_num = st.sidebar.number_input("Session Number", min_value=1, value=1)

# --- 1. Pre-Workout Readiness Score ---
st.header("📋 Readiness Check")
r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    sleep = st.slider("Sleep Quality (1-5)", 1, 5, 4)
with r_col2:
    soreness = st.slider("Soreness (1=Fresh, 5=Sore)", 1, 5, 2)
with r_col3:
    energy = st.slider("Energy (1-5)", 1, 5, 4)

ready_score = (sleep + (6 - soreness) + energy) / 3
status = "🟢 GO" if ready_score > 3.5 else "🟡 CAUTION" if ready_score > 2.5 else "🔴 RECOVER"
st.subheader(f"Status: {status}")

# --- 2. Dynamic Workout Session ---
st.divider()
st.header(f"🔥 {sport} | Session {session_num}")
drills = get_workout_template(sport)

for i, item in enumerate(drills):
    # Progressive Overload Calculation
    target_val = item['base'] + ((week_num - 1) * item['inc'])
    
    with st.expander(f"DRILL {i+1}: {item['ex']}", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            st.metric("Target", f"{target_val} {item['unit']}")
            if item['vid'] != "—":
                st.link_button("📺 Watch Form", item['vid'])
        
        with c2:
            st.write(f"**Rest:** {item['rest']}")
            if st.button(f"⏱️ Start Timer", key=f"timer_{i}"):
                time_match = re.search(r'\d+', item['rest'])
                seconds = int(time_match.group()) * 60 if 'm' in item['rest'] else int(time_match.group())
                
                t_placeholder = st.empty()
                for t in range(seconds, -1, -1):
                    mins, secs = divmod(t, 60)
                    t_placeholder.metric("Rest Remaining", f"{mins:02d}:{secs:02d}")
                    time.sleep(1)
                st.success("NEXT SET!")
                st.audio("https://www.soundjay.com/buttons/beep-01a.mp3")

        with c3:
            st.text_input("Log Result", key=f"log_{i}", placeholder="Actual reps/time")
            st.select_slider("Intensity (RPE)", options=range(1, 11), value=7, key=f"rpe_{i}")

# --- 3. Save History ---
st.divider()
if st.button("💾 SAVE SESSION DATA"):
    # Create the record
    log_data = []
    for i, item in enumerate(drills):
        res = st.session_state.get(f"log_{i}", "")
        rpe_val = st.session_state.get(f"rpe_{i}", 7)
        log_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Sport": sport, "Session": session_num, "Week": week_num,
            "Drill": item['ex'], "Result": res, "RPE": rpe_val
        })
    
    # Save to CSV
    df = pd.DataFrame(log_data)
    file = "athlete_history.csv"
    if os.path.isfile(file):
        df.to_csv(file, mode='a', header=False, index=False)
    else:
        df.to_csv(file, index=False)
        
    st.balloons()
    st.success(f"Session {session_num} Successfully Logged!")

# --- 4. Performance History & Progress ---
if os.path.isfile("athlete_history.csv"):
    st.header("📈 Progress Tracking")
    history_df = pd.read_csv("athlete_history.csv")
    
    # Filter by specific drill for chart
    drill_choice = st.selectbox("Select Drill to View History", history_df['Drill'].unique())
    drill_stats = history_df[history_df['Drill'] == drill_choice]
    
    fig = px.line(drill_stats, x='Date', y='RPE', title=f"Intensity (RPE) Over Time: {drill_choice}",
                 color_discrete_sequence=['#FFD700'])
    st.plotly_chart(fig, use_container_width=True)
