import streamlit as st
import pandas as pd
import time
import re
import os
from datetime import datetime
import plotly.express as px

# --- App Configuration ---
st.set_page_config(page_title="Sprint & Strength Pro", layout="wide")

# --- Workout Data (Complete 5-Day Program) ---
workout_data = {
    "Monday (Track - Acc.)": [
        ["Ankle dribbles", "2×20m", "2×20m", "30s", "https://youtu.be/1eX7v7S7eP0"],
        ["A-march", "2×20m", "2×20m", "30s", "https://youtu.be/83W7_9-m0Gg"],
        ["A-skips", "2×30m", "2×30m", "45s", "https://youtu.be/bk7Vp8u7XmY"],
        ["Wicket walkovers", "2×8", "3×8", "60s", "https://youtu.be/lS69U9Zp4rI"],
        ["Low-speed wickets", "2×8", "3×8", "90s", "https://youtu.be/u88Xv7z9_kI"],
        ["Speed skips (height)", "3×30m", "3×30m", "60s", "https://youtu.be/39-S6S7H-pM"],
        ["Speed skips (dist)", "3×30m", "3×30m", "60s", "—"],
        ["Wall drive accels", "3×10 ea", "3×10 ea", "60s", "—"],
        ["Hill sprints (short)", "6×20m", "7×20m", "3m", "≤3.30 / ≤3.00"],
        ["Falling starts", "4×20m", "4×20m", "2m", "3.10–3.30 / 2.85–3.00"],
        ["3-point starts", "5×30m", "5×30m", "4m", "4.00–4.25 / 3.65–3.85"],
        ["Light sled push", "5×20m", "5×20m", "2m", "≤3.60 / ≤3.20"]
    ],
    "Tuesday (Weights - Max)": [
        ["Power clean", "5×3 @70-75%", "5×3 @75-80%", "3m", "https://youtu.be/TywpOndL7LY"],
        ["Back squat", "5×5 @75-80%", "5×5 @80-85%", "4m", "https://youtu.be/ultWZbUMPL8"],
        ["Nordic curls", "3×5", "3×5", "2m", "https://youtu.be/HXT3SshP-vM"],
        ["Single-leg squats", "3×6 ea", "4×6 ea", "90s", "—"],
        ["Skater squats", "3×6 ea", "4×6 ea", "90s", "—"],
        ["RDL", "3×6", "3×6", "2m", "—"],
        ["Walking lunges", "3×8 ea", "3×8 ea", "90s", "—"],
        ["Hip thrusts", "3×8", "3×8", "2m", "—"],
        ["Standing calf raise", "3×12", "3×12", "60s", "—"],
        ["Tibialis raises", "3×15", "3×15", "45s", "—"],
        ["Hanging knee raise", "3×12", "3×12", "60s", "—"],
        ["Farmer carries", "3×30 yd", "3×30 yd", "60s", "—"]
    ],
    "Wednesday (Track - Max V)": [
        ["Ankle dribbles", "2×25m", "2×25m", "30s", "—"],
        ["Fast A-skips", "2×30m", "2×30m", "45s", "—"],
        ["Straight-leg bounds", "3×30m", "3×30m", "2m", "—"],
        ["Progressive wickets", "3×10h", "4×10h", "3m", "—"],
        ["Wicket flys", "3 reps", "3 reps", "5m", "—"],
        ["Flying 30s", "4 reps", "5 reps", "5m", "3.10–3.30 / 2.80–3.00"],
        ["Ins-and-outs", "3 reps", "3 reps", "5m", "—"],
        ["Gradual hill sprint", "4×40m", "4×40m", "3m", "≤5.15 / ≤4.65"],
        ["Moderate sled push", "4×25m", "4×25m", "3m", "≤3.80 / ≤3.40"],
        ["Power skips", "3×30m", "3×30m", "90s", "—"],
        ["Sprint-float-sprint", "3×60m", "3×60m", "5m", "—"],
        ["Strides", "2×120m", "2×130m", "90s", "16–17s / 15–16s"]
    ],
    "Thursday (Weights - Explo)": [
        ["Snatch", "5×2", "5×2 (Heavy)", "3m", "—"],
        ["Front squat", "4×4", "4×4 (Heavy)", "3m", "—"],
        ["Bulgarian split sq", "3×6 ea", "4×6 ea", "90s", "—"],
        ["Single-leg RDL", "3×6 ea", "3×6 ea", "90s", "—"],
        ["Nordic curls", "3×4", "3×4", "2m", "—"],
        ["Box jumps", "4×3", "5×3", "90s", "—"],
        ["Lateral bounds", "3×5 ea", "4×5 ea", "90s", "—"],
        ["MB overhead throws", "3×6", "4×6", "60s", "—"],
        ["MB rotational throws", "3×6 ea", "4×6 ea", "60s", "—"],
        ["Standing calf raise", "3×12", "3×12", "60s", "—"],
        ["Tibialis raises", "3×15", "3×15", "45s", "—"],
        ["Plank holds", "3×45s", "3×45s", "45s", "—"]
    ],
    "Friday (Track - Endur)": [
        ["A-skips", "2×30m", "2×30m", "45s", "—"],
        ["Speed skips (height)", "3×30m", "3×30m", "60s", "—"],
        ["Speed skips (dist)", "3×30m", "3×30m", "60s", "—"],
        ["Wicket rhythm runs", "2×12h", "3×12h", "3m", "—"],
        ["Curve wicket runs", "2×8h", "2×8h", "3m", "—"],
        ["Sprint reps (120m)", "3×120m", "4×120m", "8m", "14.5–15.5 / 13.2–14.0"],
        ["Sprint rep (150m)", "1×150m", "2×150m", "8m", "18.0–19.5 / 16.5–17.5"],
        ["Sprint-float-sprint", "2×90m", "2×90m", "6m", "—"],
        ["Hill sprints (long)", "3×40m", "3×40m", "3m", "—"],
        ["Heavy sled push", "4×20m", "4×20m", "3m", "—"],
        ["Bounds", "3×30m", "3×30m", "2m", "—"],
        ["Tempo strides", "2×150m", "2×160m", "90s", "23–26s / 21–24s"]
    ]
}

# --- Helper Functions ---
def get_personal_records():
    if os.path.isfile("workout_history.csv"):
        df = pd.read_csv("workout_history.csv")
        df['Value'] = df['Actual'].str.extract(r'(\d+\.?\d*)').astype(float)
        pr_list = {}
        for exercise in df['Exercise'].unique():
            ex_data = df[df['Exercise'] == exercise].dropna(subset=['Value'])
            if ex_data.empty: continue
            if any(word in exercise.lower() for word in ['sprint', 'fly', 'start', '30m', 'hill']):
                pr_val = ex_data['Value'].min()
                unit = "s"
            else:
                pr_val = ex_data['Value'].max()
                unit = "kg/lb"
            pr_list[exercise] = f"{pr_val}{unit}"
        return pr_list
    return {}

# --- UI Header & PRs ---
st.title("🏃‍♂️ Elite Performance Tracker")
prs = get_personal_records()
if prs:
    st.subheader("🏆 Personal Records")
    cols = st.columns(min(len(prs), 4))
    for idx, (ex, val) in enumerate(list(prs.items())[:4]):
        cols[idx].metric(ex, val)

# --- Navigation ---
day = st.sidebar.selectbox("Select Training Day", list(workout_data.keys()))
week = st.sidebar.radio("Select Week", ["Week 1", "Week 2"])

# --- Exercise Display ---
st.header(f"Session: {day}")
for i, exercise in enumerate(workout_data[day]):
    with st.expander(f"{i+1}. {exercise[0]}", expanded=True):
        col1, col2, col3 = st.columns([1, 1, 1])
        target = exercise[1] if week == "Week 1" else exercise[2]
        
        with col1:
            st.metric("Target", target)
            if len(exercise) > 4 and "http" in exercise[4]:
                st.link_button("📺 Watch Form", exercise[4])
        
        with col2:
            st.write(f"**Rest:** {exercise[3]}")
            if st.button(f"⏱️ Start Timer", key=f"t_{i}"):
                match = re.search(r'\d+', exercise[3])
                sec = int(match.group()) * 60 if 'm' in exercise[3] else int(match.group())
                ph = st.empty()
                for t in range(sec, -1, -1):
                    m, s = divmod(t, 60)
                    ph.metric("Rest Remaining", f"{m:02d}:{s:02d}")
                    time.sleep(1)
                st.success("Time to Go!")
                st.audio("https://www.soundjay.com/buttons/beep-01a.mp3")

        with col3:
            st.text_input("Log Result", key=f"log_{day}_{i}", placeholder="e.g. 3.12s or 100kg")

# --- Save Session ---
if st.button("💾 Complete & Save Session"):
    session_results = []
    for i, exercise in enumerate(workout_data[day]):
        res = st.session_state.get(f"log_{day}_{i}", "")
        if res:
            session_results.append({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Day": day, "Exercise": exercise[0], "Week": week, "Actual": res
            })
    
    if session_results:
        df_new = pd.DataFrame(session_results)
        if os.path.isfile("workout_history.csv"):
            df_old = pd.read_csv("workout_history.csv")
            pd.concat([df_old, df_new]).to_csv("workout_history.csv", index=False)
        else:
            df_new.to_csv("workout_history.csv", index=False)
        st.balloons()
        st.success("Session Saved!")

# --- Analytics Section ---
if os.path.isfile("workout_history.csv"):
    st.divider()
    st.header("📈 Weekly Analytics")
    df_an = pd.read_csv("workout_history.csv")
    df_an['Vol'] = df_an['Actual'].str.extract(r'(\d+)').astype(float)
    df_an['Date'] = pd.to_datetime(df_an['Date'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("Sprinting Volume (Meters)")
        track_v = df_an[df_an['Day'].str.contains("Track")].groupby('Date')['Vol'].sum().reset_index()
        st.plotly_chart(px.bar(track_v, x='Date', y='Vol'), use_container_width=True)
    with c2:
        st.write("Lifting Intensity (Sets)")
        lift_v = df_an[df_an['Day'].str.contains("Weights")].groupby('Date')['Vol'].count().reset_index()
        st.plotly_chart(px.line(lift_v, x='Date', y='Vol'), use_container_width=True)