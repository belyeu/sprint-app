import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None
if 'active_sport' not in st.session_state: st.session_state.active_sport = ""

# --- 2. SIDEBAR (DATE MOVED HERE) ---
with st.sidebar:
    # High-Contrast Date/Time Card
    st.markdown(f"""
    <div style="background-color:#F8FAFC; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#000000; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#1E293B; margin:0; font-weight:bold; letter-spacing:1px;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    location = st.selectbox("Location", ["Gym", "Softball Field", "Batting Cages", "Track", "Weight Room"])
    sport_choice = st.selectbox("Sport Database", ["Basketball", "Softball", "Track", "General"])
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = None

# --- 3. CUSTOM CSS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #0F172A !important; }}
    [data-testid="stSidebar"] {{ background-color: #0F172A !important; border-right: 1px solid #1E293B; }}
    
    /* SIDEBAR LABELS TO BLACK */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] span {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}

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

# --- 4. DATABASE (ALL WITH SETS/REPS/TIME) ---
def get_vault():
    return {
        "Basketball": [
            {"ex": "Iverson Cross", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Wide deceptive step-across.", "focus": ["Width", "Low Hips"]},
            {"ex": "Shammgod", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "15s", "desc": "Push out R, pull back L.", "focus": ["Extension", "Speed"]},
            {"ex": "Pocket Pulls", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Pull ball to hip pocket.", "focus": ["Security", "Wrist Snap"]},
            {"ex": "Trae Young Pullback", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "18s", "desc": "Lunge forward and snap back.", "focus": ["Deceleration", "Balance"]},
            {"ex": "V-Dribble (R/L)", "sets": 3, "base": 40, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "One-handed 'V' shape.", "focus": ["Pound Force"]},
            {"ex": "Inside Out Jab", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Fake move with heavy jab.", "focus": ["Head Fake"]},
            {"ex": "Spin to Post", "sets": 3, "base": 8, "unit": "reps", "rest": 45, "time_goal": "22s", "desc": "Drive R, spin to turn back.", "focus": ["Pivot Accuracy"]},
            {"ex": "Stutter Step", "sets": 3, "base": 20, "unit": "m", "rest": 30, "time_goal": "12s", "desc": "Chop feet to freeze defender.", "focus": ["Foot Frequency"]},
            {"ex": "Behind Back Stop", "sets": 3, "base": 8, "unit": "reps", "rest": 45, "time_goal": "15s", "desc": "Sprint into behind-back halt.", "focus": ["Body Control"]},
            {"ex": "Double Tap Cross", "sets": 3, "base": 10, "unit": "reps", "rest": 30, "time_goal": "14s", "desc": "Drop and tap twice before cross.", "focus": ["Hand Speed"]},
            {"ex": "High/Low Walking", "sets": 2, "base": 20, "unit": "m", "rest": 30, "time_goal": "20s", "desc": "3 High, 3 Low; walking forward.", "focus": ["Rhythm"]},
            {"ex": "Crossover-Spin", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "25s", "desc": "Link cross and spin.", "focus": ["Fluidity"]}
        ],
        "Softball": [
            {"ex": "Shuffle Step Throw", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "40s", "desc": "Instep to instep throw.", "focus": ["Accuracy"]},
            {"ex": "Power Step", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "35s", "desc": "Instep to ball; move around.", "focus": ["Wrap Around Tag"]},
            {"ex": "Jam Step Backhand", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Glove foot steps with ball.", "focus": ["Drop And Up"]},
            {"ex": "Short Hop Drills", "sets": 4, "base": 20, "unit": "reps", "rest": 30, "time_goal": "45s", "desc": "Make hops shorter; soft hands.", "focus": ["Glove Presentation"]},
            {"ex": "Dart Throws", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Elbow, wrist, finger snap.", "focus": ["Quick Release"]},
            {"ex": "Tripod Grounders", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Bare hand down; eyes behind.", "focus": ["Eye Alignment"]},
            {"ex": "Fence Work", "sets": 3, "base": 8, "unit": "reps", "rest": 60, "time_goal": "40s", "desc": "Feel fence; climb for catch.", "focus": ["Spatial Awareness"]},
            {"ex": "Do or Die Pro", "sets": 4, "base": 10, "unit": "reps", "rest": 45, "time_goal": "30s", "desc": "Throw on run; full speed.", "focus": ["Momentum Transfer"]},
            {"ex": "Glove Flip", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Using glove to flip ball.", "focus": ["Quick Transfer"]},
            {"ex": "Catcher Blocking", "sets": 4, "base": 15, "unit": "reps", "rest": 45, "time_goal": "40s", "desc": "Center of ball shift.", "focus": ["Body Angle"]},
            {"ex": "Slide Dives", "sets": 3, "base": 8, "unit": "reps", "rest": 60, "time_goal": "35s", "desc": "Knees take you down low.", "focus": ["Body Control"]},
            {"ex": "3/4 Sway Throw", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Bow & arrow tilt mechanics.", "focus": ["Core Strength"]}
        ],
        "Track": [
            {"ex": "Pogo Jumps", "sets": 3, "base": 20, "unit": "reps", "rest": 60, "time_goal": "15s", "desc": "Ankle Stiffness focus.", "focus": ["Elasticity"]},
            {"ex": "A-March", "sets": 3, "base": 20, "unit": "m", "rest": 45, "time_goal": "12s", "desc": "Posture & Dorsiflexion.", "focus": ["Toe Up"]},
            {"ex": "Wall Drive Accels", "sets": 5, "base": 5, "unit": "reps", "rest": 90, "time_goal": "10s", "desc": "Drive Phase Mechanics.", "focus": ["Lean"]},
            {"ex": "Flying 30s", "sets": 4, "base": 30, "unit": "m", "rest": 180, "time_goal": "4s", "desc": "Pure Top-End Speed.", "focus": ["Relaxation"]},
            {"ex": "Wicket Flys", "sets": 4, "base": 40, "unit": "m", "rest": 120, "time_goal": "6s", "desc": "Max Velocity Maintenance.", "focus": ["Frequency"]},
            {"ex": "Straight-Leg Bounds", "sets": 3, "base": 30, "unit": "m", "rest": 90, "time_goal": "8s", "desc": "Glute/Hamstring Snap.", "focus": ["Active Foot"]},
            {"ex": "Hill Sprints", "sets": 6, "base": 30, "unit": "m", "rest": 120, "time_goal": "5s", "desc": "Force vs Gravity.", "focus": ["Knee Drive"]},
            {"ex": "Tempo Strides", "sets": 4, "base": 100, "unit": "m", "rest": 60, "time_goal": "15s", "desc": "Recovery & Form Work.", "focus": ["Technique"]}
        ],
        "General": [
            {"ex": "Bulgarian Split Squat", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "time_goal": "45s", "desc": "Unilateral Strength.", "focus": ["Knee Tracking"]},
            {"ex": "Nordic Curls", "sets": 3, "base": 6, "unit": "reps", "rest": 90, "time_goal": "30s", "desc": "Eccentric Hamstring Safety.", "focus": ["Slow Descent"]},
            {"ex": "Power Clean", "sets": 5, "base": 3, "unit": "reps", "rest": 120, "time_goal": "Explosive", "desc": "Rate of Force Development.", "focus": ["Extension"]},
            {"ex": "Pallof Press", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "time_goal": "30s", "desc": "Anti-rotation core hold.", "focus": ["Core Bracing"]},
            {"ex": "Box Jumps", "sets": 4, "base": 5, "unit": "reps", "rest": 60, "time_goal": "15s", "desc": "Vertical Displacement.", "focus": ["Soft Landing"]},
            {"ex": "Farmer Carries", "sets": 3, "base": 40, "unit": "m", "rest": 60, "time_goal": "35s", "desc": "Grip & Core Anti-Flexion.", "focus": ["Posture"]},
            {"ex": "Spiderman w/ Reach", "sets": 2, "base": 10, "unit": "reps", "rest": 30, "time_goal": "60s", "desc": "Hip & Thoracic mobility.", "focus": ["Opening Hips"]},
            {"ex": "Deadbugs", "sets": 3, "base": 12, "unit": "reps", "rest": 30, "time_goal": "45s", "desc": "Spinal Control.", "focus": ["Lower Back Flush"]}
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
            <span style="color:#60A5FA">Time Goal:</span> {drill['time_goal']}
        </div>
        """, unsafe_allow_html=True)
        st.write(f"_{drill['desc']}_")
        
        st.markdown("**Complete Sets:**")
        set_cols = st.columns(drill['sets'])
        for s in range(drill['sets']):
            set_cols[s].checkbox(f"S{s+1}", key=f"s_{i}_{s}")
            
    with col2:
        st.markdown(f"⏱️ **Recommended Rest: {drill['rest']}s**")
        if st.button(f"START REST TIMER", key=f"t_{i}"):
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
        st.markdown("🎥 **Action**")
        st.button("Watch Demo", key=f"d_{i}")
        st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"u_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "loc": location})
    st.balloons()
    st.success("Session saved!")
