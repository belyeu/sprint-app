import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime, date

# --- 1. Mobile-Optimized High-Contrast Theme (Dark Green & Gold) ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #013220 !important; color: #ffffff !important; }
    
    /* DRILL HEADER - High Visibility Gold */
    .drill-header {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: #FFD700 !important;
        text-transform: uppercase;
        margin-bottom: 10px;
        margin-top: 35px;
        font-family: 'Arial Black', sans-serif;
        border-left: 12px solid #FFD700;
        padding-left: 20px;
        background-color: #004d26;
        border-radius: 0 10px 10px 0;
    }
    
    /* MOBILE VISIBILITY: Stats Labels */
    .stat-label { 
        font-size: 18px !important; 
        font-weight: 800 !important; 
        color: #FFD700 !important; 
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    
    .stat-value { 
        font-size: 40px !important; 
        font-weight: 900 !important; 
        color: #FFFFFF !important; 
        margin-top: -5px;
    }

    /* Timer Text */
    .timer-text {
        font-size: 85px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        background: #002d16;
        border-radius: 12px;
        border: 4px solid #FFD700;
        padding: 15px;
    }

    /* Buttons - Large Tap Targets for Mobile */
    .stButton>button { 
        background-color: #FFD700 !important; 
        color: #013220 !important; 
        border-radius: 12px !important; 
        font-weight: 900 !important; 
        width: 100%; 
        height: 75px !important;
        font-size: 24px !important;
        border: 3px solid #DAA520 !important;
    }

    /* Checklist & Inputs Visibility */
    .stCheckbox label { font-size: 20px !important; font-weight: 700 !important; color: #FFFFFF !important; }
    .coach-notes { background-color: #ffd70022; padding: 15px; border-radius: 8px; border-left: 5px solid #FFD700; margin-bottom: 15px; color: #FFFFFF; }
    .recovery-card { background-color: #004d26; border: 3px solid #FFD700; padding: 25px; border-radius: 15px; margin-top: 30px; }

    /* Custom Sidebar Card for Streak */
    .sidebar-card {
        background-color: #FFD700;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 4px solid #DAA520;
        margin-bottom: 20px;
    }

    @media (max-width: 600px) {
        .timer-text { font-size: 55px !important; }
        .stat-value { font-size: 32px !important; }
        .drill-header { font-size: 24px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Multi-Sport Drill Database ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "base": 60, "inc": 15, "unit": "sec", "rest": 30, "type": "cond", "desc": "Hard, explosive dribbles at hip, knee, and ankle height. Keep eyes up.", "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Power Dribble", "Eyes Up"]},
            {"ex": "FIGURE 8 SERIES", "base": 90, "inc": 20, "unit": "sec", "rest": 30, "type": "cond", "desc": "Low dribbles in a figure-8 pattern around legs.", "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Fingertip Control", "Low Center", "No Tangles"]},
            {"ex": "STATIONARY CROSSOVER", "base": 100, "inc": 25, "unit": "reps", "rest": 45, "type": "power", "desc": "Wide crossovers outside the frame of your body. Snap the ball across.", "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "eval": ["Wide Snap", "Rhythm", "Low Hips"]},
            {"ex": "MIKAN SERIES", "base": 50, "inc": 10, "unit": "makes", "rest": 60, "type": "power", "desc": "Continuous layups alternating hands.", "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["High Finish", "Footwork", "Soft Touch"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "base": 40, "inc": 10, "unit": "meters", "rest": 30, "type": "cond", "desc": "Quick steps with toes up.", "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Ankle Drive", "Tall Posture"]},
            {"ex": "A-SKIP", "base": 60, "inc": 10, "unit": "meters", "rest": 60, "type": "power", "desc": "Aggressive foot strike under center of mass.", "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Action", "Knee Drive"]}
        ],
        "Softball": [
            {"ex": "TEE SERIES", "base": 50, "inc": 15, "unit": "swings", "rest": 60, "type": "power", "desc": "Focus on hand path. Hit to all fields.", "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact", "Balanced Stance"]},
            {"ex": "GLOVE WORK (KNEES)", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power", "desc": "Develop soft hands and quick transfers.", "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Soft Hands", "Quick Transfer", "Glove Position"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "base": 15, "inc": 3, "unit": "reps", "rest": 120, "type": "power", "desc": "Hold weight at chest. Sit back into hips.", "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up", "Heels Down"]},
            {"ex": "PUSHUPS", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power", "desc": "Full range of motion.", "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout", "Chest to Floor"]}
        ]
    }
    return workouts.get(sport, [])

# --- 3. Sidebar ---
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
if 'streak' not in st.session_state: st.session_state.streak = 1
st.sidebar.markdown(f'<p style="color:#013220; margin:0; font-weight:800; font-size:16px;">STREAK</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="color:#013220; font-size:44px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)

# Difficulty Scaling
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 4. Main App UI ---
st.markdown(f"<h1>{sport_choice} | {difficulty}</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

if 'session_saved' not in st.session_state: st.session_state.session_saved = False

for i, item in enumerate(drills):
    drill_key = f"{sport_choice}_{i}"
    if drill_key not in st.session_state: st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    
    # Target and Progress Display (Mobile Optimized)
    c1, c2 = st.columns(2)
    with c1:
        target_val = int((item['base'] + ((week_num - 1) * item['inc'])) * target_mult)
        st.markdown(f'<p class="stat-label">Target</p><p class="stat-value">{target_val} {item["unit"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="stat-label">Set Progress</p><p class="stat-value">{st.session_state[drill_key]} / {item.get("sets", 4)}</p>', unsafe_allow_html=True)

    # Coach's Notes Section
    st.markdown(f'<div class="coach-notes"><b>Coach\'s Notes:</b> {item["desc"]}</div>', unsafe_allow_html=True)

    # Action Buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"SET DONE ✅", key=f"done_{i}"):
            st.session_state[drill_key] += 1
            st.rerun()
    with col_b:
        if st.button(f"START REST ⏱️", key=f"rest_{i}"):
            final_rest = int(item['rest'] * rest_mult) if item['type'] == 'power' else int(item['rest'] / rest_mult)
            ph = st.empty()
            for t in range(final_rest, -1, -1):
                m, s = divmod(t, 60)
                ph.markdown(f'<p class="timer-text">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state[drill_key] += 1
            st.rerun()

    # Logging, RPE & Checklist
    st.markdown("### 📋 COACH'S EVALUATION")
    eval_cols = st.columns(2)
    for idx, criteria in enumerate(item['eval']):
        eval_cols[idx % 2].checkbox(criteria, key=f"check_{drill_key}_{idx}")
    
    st.text_input("Log Result / Notes", key=f"log_{i}")
    st.select_slider("Intensity (RPE)", options=range(1, 11), value=8, key=f"rpe_{i}")

    with st.expander("🎥 WATCH DEMO & UPLOAD"):
        st.video(item['vid'])
        st.file_uploader("Upload Video", type=["mp4", "mov"], key=f"up_{i}")

st.divider()

if st.button("💾 SAVE SESSION DATA"):
    st.session_state.session_saved = True
    st.balloons()

if st.session_state.session_saved:
    st.markdown("""
        <div class="recovery-card">
            <h3>✅ SESSION COMPLETE! RECOVERY PROTOCOL:</h3>
            <ul>
                <li><b>Hydration:</b> Consume 16-24oz of water with electrolytes.</li>
                <li><b>Nutrition:</b> Eat a 3:1 Carb-to-Protein snack/meal within 45 mins.</li>
                <li><b>Soft Tissue:</b> 5-10 mins of foam rolling or static stretching.</li>
                <li><b>Mental:</b> Log one thing you did well and one to improve.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
