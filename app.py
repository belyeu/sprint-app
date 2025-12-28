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

# --- 2. SIDEBAR (BLACK LABELS & DATE) ---
with st.sidebar:
    # Date/Time Card
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

# --- 4. FULL MASTER DATABASE ---
def get_vault():
    return {
        "Basketball": [
            {"ex": "Ball Slaps & Wraps", "sets": 3, "base": 30, "unit": "sec", "rest": 15, "time_goal": "Max Speed", "desc": "Continuous wraps around head, waist, and knees.", "focus": ["Fingertip Control"]},
            {"ex": "Iverson Cross", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Wide deceptive step-across move.", "focus": ["Low Hips", "Width"]},
            {"ex": "Shammgod", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "15s", "desc": "Push ball out with R, pull back with L.", "focus": ["Extension", "Speed"]},
            {"ex": "Pocket Pulls", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Dribble and pull ball hard into hip pocket.", "focus": ["Security", "Wrist Snap"]},
            {"ex": "Mikan Drill", "sets": 3, "base": 20, "unit": "makes", "rest": 45, "time_goal": "40s", "desc": "Alternate side layups under the rim.", "focus": ["Footwork", "High Release"]},
            {"ex": "Trae Young Pullback", "sets": 3, "base": 10, "unit": "reps", "rest": 45, "time_goal": "18s", "desc": "Lunge forward into a hard snap-back dribble.", "focus": ["Deceleration"]},
            {"ex": "Zig-Zag Pull-Up", "sets": 4, "base": 6, "unit": "makes", "rest": 60, "time_goal": "Fluid", "desc": "Zig-zag dribble into a mid-range jumper.", "focus": ["Stop on a Dime"]},
            {"ex": "V-Dribble (R/L)", "sets": 3, "base": 40, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Stationary one-handed 'V' shape dribble.", "focus": ["Pound Force"]},
            {"ex": "Figure 8 Dribble", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Low dribble through and around legs.", "focus": ["Eyes Up"]},
            {"ex": "Inside Out Jab", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "In-and-out move paired with a heavy jab step.", "focus": ["Head Fake"]},
            {"ex": "Spin to Post", "sets": 3, "base": 8, "unit": "reps", "rest": 45, "time_goal": "22s", "desc": "Drive, then spin to turn back toward the hoop.", "focus": ["Pivot Accuracy"]},
            {"ex": "Free Throw Fatigue", "sets": 5, "base": 10, "unit": "reps", "rest": 30, "time_goal": "8/10", "desc": "Shoot 10 free throws while breathing heavy.", "focus": ["Routine"]}
        ],
        "Softball": [
            {"ex": "Kneeling Glove Work", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "time_goal": "Clean", "desc": "Forehand and backhand picks from knees.", "focus": ["Soft Hands"]},
            {"ex": "Shuffle Step Throw", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "40s", "desc": "Field and shuffle toward target for throw.", "focus": ["Accuracy", "Footwork"]},
            {"ex": "Short Hop Drills", "sets": 4, "base": 20, "unit": "reps", "rest": 30, "time_goal": "45s", "desc": "Partner throws short hops; field at the bounce.", "focus": ["Glove Presentation"]},
            {"ex": "Jam Step Backhand", "sets": 4, "base": 12, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Backhand fielding where glove foot steps.", "focus": ["Stay Low"]},
            {"ex": "Dart Throws", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "time_goal": "25s", "desc": "Focus on elbow lead and wrist snap.", "focus": ["Quick Release"]},
            {"ex": "Tripod Grounders", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "30s", "desc": "Bare hand down; eyes behind the ball.", "focus": ["Eye Alignment"]},
            {"ex": "Fence Work", "sets": 3, "base": 8, "unit": "reps", "rest": 60, "time_goal": "40s", "desc": "Drill for tracking and catching at the wall.", "focus": ["Spatial Awareness"]},
            {"ex": "Do or Die Pro", "sets": 4, "base": 10, "unit": "reps", "rest": 45, "time_goal": "30s", "desc": "Charge the ball and throw on the run.", "focus": ["Momentum"]},
            {"ex": "Glove Flip", "sets": 3, "base": 15, "unit": "reps", "rest": 30, "time_goal": "20s", "desc": "Quick flip using only the glove hand.", "focus": ["Precision"]},
            {"ex": "Catcher Blocking", "sets": 4, "base": 15, "unit": "reps", "rest": 45, "time_goal": "40s", "desc": "Center of ball shift and drop.", "focus": ["Body Angle"]},
            {"ex": "Slide Dives", "sets": 3, "base": 8, "unit": "reps", "rest": 60, "time_goal": "Controlled", "desc": "Infield diving technique into sliding catch.", "focus": ["Safety"]},
            {"ex": "Tee Extension", "sets": 4, "base": 15, "unit": "swings", "rest": 60, "time_goal": "Solid", "desc": "Focus on full arm extension at contact.", "focus": ["Bat Path"]}
        ],
        "Track": [
            {"ex": "Pogo Jumps", "sets": 3, "base": 20, "unit": "reps", "rest": 60, "time_goal": "15s", "desc": "Vertical jumps focused on ankle stiffness.", "focus": ["Short Ground Contact"]},
            {"ex": "A-March", "sets": 3, "base": 20, "unit": "m", "rest": 45, "time_goal": "12s", "desc": "Exaggerated marching for posture.", "focus": ["Toe Up", "Dorsiflexion"]},
            {"ex": "Wall Drive Accels", "sets": 5, "base": 5, "unit": "reps", "rest": 90, "time_goal": "10s", "desc": "Drive phase drills leaning against wall.", "focus": ["45 Degree Lean"]},
            {"ex": "Flying 30s", "sets": 4, "base": 30, "unit": "m", "rest": 180, "time_goal": "4.0s", "desc": "Full speed sprint after a 20m build-up.", "focus": ["Max Velocity"]},
            {"ex": "Wicket Flys", "sets": 4, "base": 40, "unit": "m", "rest": 120, "time_goal": "6.0s", "desc": "Sprinting over mini-hurdles (wickets).", "focus": ["Frequency", "Step Pattern"]},
            {"ex": "Straight-Leg Bounds", "sets": 3, "base": 30, "unit": "m", "rest": 90, "time_goal": "8s", "desc": "Bouncing with stiff legs to engage glutes.", "focus": ["Active Foot Strike"]},
            {"ex": "Hill Sprints", "sets": 6, "base": 30, "unit": "m", "rest": 120, "time_goal": "5.5s", "desc": "Incline sprints for power development.", "focus": ["Knee Drive"]},
            {"ex": "Tempo Strides", "sets": 4, "base": 100, "unit": "m", "rest": 60, "time_goal": "15s", "desc": "80% effort runs focused on perfect form.", "focus": ["Fluidity"]}
        ],
        "General": [
            {"ex": "Power Clean", "sets": 5, "base": 3, "unit": "reps", "rest": 120, "time_goal": "Explosive", "desc": "Full body explosive pull from floor to chest.", "focus": ["Full Extension"]},
            {"ex": "Bulgarian Split Squat", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "time_goal": "45s", "desc": "Single-leg squat with rear foot elevated.", "focus": ["Knee Stability"]},
            {"ex": "Nordic Curls", "sets": 3, "base": 6, "unit": "reps", "rest": 90, "time_goal": "30s", "desc": "Slow eccentric lowering of the torso.", "focus": ["Hamstring Strength"]},
            {"ex": "Pallof Press", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "time_goal": "30s", "desc": "Anti-rotation core hold with resistance.", "focus": ["No Hip Shift"]},
            {"ex": "Box Jumps", "sets": 4, "base": 5, "unit": "reps", "rest": 60, "time_goal": "15s", "desc": "Max height jumps onto platform.", "focus": ["Soft Landing"]},
            {"ex": "Farmer Carries", "sets": 3, "base": 40, "unit": "m", "rest": 60, "time_goal": "35s", "desc": "Heavy walking for grip and core stability.", "focus": ["Shoulder Position"]},
            {"ex": "Spiderman w/ Reach", "sets": 2, "base": 10, "unit": "reps", "rest": 30, "time_goal": "60s", "desc": "Deep lunge with thoracic rotation.", "focus": ["Hip Mobility"]},
            {"ex": "Deadbugs", "sets": 3, "base": 12, "unit": "reps", "rest": 30, "time_goal": "45s", "desc": "Core stability maintaining flat lower back.", "focus": ["Lower Back Flush"]}
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
st.title(f"🔥 {difficulty} {sport_choice} Training Session")
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
        
        st.markdown("🎯 **Coach's Evaluation**")
        for f in drill["focus"]:
            st.checkbox(f, key=f"f_{i}_{f}")

    with col3:
        st.markdown("🎥 **Action**")
        st.button("Watch Demo", key=f"d_{i}")
        st.file_uploader("Upload Progress Clip", type=["mp4", "mov"], key=f"u_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "loc": location})
    st.balloons()
    st.success("Session saved to Performance History!")
