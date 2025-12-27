import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

# --- 1. Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #013220; color: #ffffff; }
    .drill-header {
        font-size: 34px !important; font-weight: 900 !important; color: #FFD700 !important;
        text-transform: uppercase; margin-top: 30px; font-family: 'Arial Black', sans-serif;
        border-left: 10px solid #FFD700; padding-left: 20px;
    }
    .timer-text {
        font-size: 85px !important; font-weight: bold !important; color: #FFD700 !important;
        text-align: center; font-family: 'Courier New', Courier, monospace;
        background: #004d26; border-radius: 12px; border: 4px solid #FFD700; padding: 15px;
    }
    .set-badge {
        background-color: #FFD700; color: #013220; padding: 10px 20px;
        border-radius: 30px; font-weight: 900; font-size: 18px; display: inline-block; margin-bottom: 10px;
    }
    .streak-card {
        background: linear-gradient(135deg, #FFD700 0%, #DAA520 100%);
        color: #013220; padding: 15px; border-radius: 10px; text-align: center;
        font-weight: 900; margin-bottom: 20px; border: 2px solid #ffffff;
    }
    .coach-eval {
        background-color: #004d26; border: 2px dashed #FFD700;
        padding: 20px; border-radius: 10px; margin-top: 20px;
    }
    .pro-status-box {
        background-color: #1a1a1a; border: 2px solid #FFD700; color: #ffffff;
        padding: 20px; border-radius: 10px; margin-top: 15px;
    }
    .stButton>button { 
        background-color: #FFD700; color: #013220; border-radius: 10px; 
        font-weight: bold; border: 2px solid #DAA520; width: 100%; height: 60px; font-size: 22px;
    }
    .stMetric { background-color: #004d26; padding: 20px; border-radius: 12px; border: 3px solid #FFD700; }
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
        {"ex": "POUND SERIES", "base_reps": 30, "sets": 4, "inc": 5, "unit": "sec", "pro_bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "desc": "Hard, explosive dribbles at various heights."},
        {"ex": "MIKAN SERIES", "base_reps": 25, "sets": 4, "inc": 5, "unit": "makes", "pro_bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "desc": "Rhythm and touch finishing around the rim."},
        {"ex": "STATIONARY CROSSOVER", "base_reps": 50, "sets": 4, "inc": 10, "unit": "reps", "pro_bench": 400, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "desc": "Wide, aggressive crossovers with eyes up."}
    ]

# --- 4. Sidebar ---
st.sidebar.header("🥇 ATHLETE PROFILE")
st.sidebar.markdown(f"""
    <div class="streak-card">
        <span style="font-size: 14px;">CURRENT STREAK</span><br>
        <span style="font-size: 32px;">{st.session_state.streak} DAYS</span>
    </div>
""", unsafe_allow_html=True)

sport = st.sidebar.selectbox("Choose Sport", ["Basketball"])
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
difficulty = st.sidebar.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")

target_mult = 1.0 if difficulty == "Standard" else 1.5 if difficulty == "Elite" else 2.0

# --- 5. Main Workout Hub ---
st.header("🔥 PRO-LEVEL PERFORMANCE HUB")
drills = get_workout_template()

for i, item in enumerate(drills):
    drill_key = f"drill_{i}"
    if drill_key not in st.session_state.set_counters: st.session_state.set_counters[drill_key] = 0

    reps_per_set = int((item['base_reps'] + ((week_num - 1) * item['inc'])) * target_mult)
    total_goal = reps_per_set * item['sets']
    
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    current_set = st.session_state.set_counters[drill_key]
    st.markdown(f'<div class="set-badge">SET {current_set} / {item["sets"]} COMPLETE</div>', unsafe_allow_html=True)
    
    with st.expander("DRILL DASHBOARD & VIDEO ANALYSIS", expanded=True):
        # Video Comparison Section
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("**PRO DEMO**")
            st.video(item['vid'])
        with col_v2:
            st.markdown("**YOUR GALLERY**")
            uploaded_video = st.file_uploader("Upload from Phone", type=["mp4", "mov"], key=f"up_{i}")
            if uploaded_video: st.video(uploaded_video)
            else: st.info("Tap to select video from gallery")

        # Coach's Evaluation
        st.markdown('<div class="coach-eval">', unsafe_allow_html=True)
        st.subheader("📋 COACH'S SELF-EVALUATION")
        q1 = st.checkbox("Back straight & posture neutral?", key=f"q1_{i}")
        q2 = st.checkbox("Game-speed intensity maintained?", key=f"q2_{i}")
        notes = st.text_area("Adjustment for next set:", key=f"note_{i}", placeholder="e.g., Cross the ball wider...")
        st.markdown('</div>', unsafe_allow_html=True)

        # Controls & Logging
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Target", f"{reps_per_set} x {item['sets']}")
            if st.button(f"✅ Set Done", key=f"done_{i}"):
                if st.session_state.set_counters[drill_key] < item['sets']:
                    st.session_state.set_counters[drill_key] += 1
                    st.rerun()
        with c2:
            if st.button(f"⏱️ Rest Timer", key=f"timer_{i}"):
                ph = st.empty()
                for t in range(30, -1, -1):
                    ph.markdown(f'<p class="timer-text">{t:02d}s</p>', unsafe_allow_html=True)
                    time.sleep(1)
                st.session_state.set_counters[drill_key] = min(st.session_state.set_counters[drill_key] + 1, item['sets'])
                st.rerun()
        with c3:
            val = st.number_input(f"Total {item['unit']}", key=f"val_{i}", min_value=0)
            rpe = st.select_slider("Intensity (1-10)", options=range(1,11), value=7, key=f"rpe_{i}")
            st.session_state.session_history[item['ex']] = {"val": val, "rpe": rpe}

st.divider()

# --- 6. Final Save & Feedback ---
if st.button("💾 FINISH SESSION & UPDATE STREAK"):
    update_streak()
    st.balloons()
    st.subheader("📊 ELITE PERFORMANCE FEEDBACK")
    
    for item in drills:
        data = st.session_state.session_history.get(item['ex'], {"val": 0, "rpe": 7})
        percent = min(int((data['val'] / item['pro_bench']) * 100), 100)
        
        feedback = "🎯 Optimal training zone."
        if data['rpe'] <= 5: feedback = "⚠️ Stimulus too low for pro growth."
        elif data['rpe'] >= 9: feedback = "🔥 Elite effort! Prioritize recovery."

        st.markdown(f"""
            <div class="pro-status-box">
                <h4>{item['ex']}</h4>
                <p><b>Pro-Benchmark Completion:</b> {percent}%</p>
                <p><i>{feedback}</i></p>
            </div>
        """, unsafe_allow_html=True)
