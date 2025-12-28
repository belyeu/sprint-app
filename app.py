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

# Persistent State
if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None

# Sidebar Features
st.sidebar.markdown("### 🏟️ SESSION CONFIG")
location = st.sidebar.selectbox("Location", ["Gym", "Softball Field", "Batting Cages", "Track", "Weight Room"])
sport_choice = st.sidebar.selectbox("Sport Database", ["Basketball", "Softball", "Track", "General"])
difficulty = st.sidebar.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

# Theme Logic
if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}
h1, h2, h3, p, span, label, li {{ color: {text} !important; }}
.drill-header {{
    font-size: 18px !important; font-weight: 800 !important;
    color: {accent} !important; background-color: {header}; 
    border-left: 6px solid {accent}; padding: 10px; margin-top: 15px; border-radius: 4px;
}}
</style>
""", unsafe_allow_html=True)

# --- 2. THE COMPLETE VAULT (RAW DATA) ---
def load_all_data():
    return {
        "Basketball": [
            {"ex": "High/Low Walking (R/L)", "desc": "3 High, 3 Low; walking forward.", "base": 20, "unit": "m", "rest": 30, "focus": ["Rhythm", "Wrist Snap", "Eye Level"], "demo": "https://www.youtube.com"},
            {"ex": "Iverson Cross", "desc": "Wide deceptive step-across.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Width", "Deception", "Low Hips"], "demo": "https://www.youtube.com"},
            {"ex": "Shammgod", "desc": "Push out R, pull back L.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Extension", "Change of Pace"], "demo": "https://www.youtube.com"},
            {"ex": "Pocket Pulls", "desc": "Pull ball to hip pocket.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Security", "Control"], "demo": "https://www.youtube.com"},
            {"ex": "Trae Young Pullback", "desc": "Lunge forward and snap back.", "base": 12, "unit": "reps", "rest": 40, "focus": ["Deceleration", "Balance"], "demo": "https://www.youtube.com"},
            {"ex": "Spin to Post", "desc": "Drive R, spin to turn back.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Pivot Accuracy"], "demo": "https://www.youtube.com"},
            {"ex": "Double Tap", "desc": "Drop and tap twice before cross.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Hand Speed"], "demo": "https://www.youtube.com"},
            {"ex": "V-Dribble (R/L)", "desc": "One-handed 'V' shape.", "base": 50, "unit": "reps", "rest": 30, "focus": ["Pound Force"], "demo": "https://www.youtube.com"},
            {"ex": "Stutter Step", "desc": "Chop feet to freeze defender.", "base": 20, "unit": "m", "rest": 30, "focus": ["Foot Frequency"], "demo": "https://www.youtube.com"},
            {"ex": "Inside Out Jab", "desc": "Fake move with heavy jab.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Head Fake"], "demo": "https://www.youtube.com"},
            {"ex": "Retreat Inside Out", "desc": "Create space, then fake.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Space Creation"], "demo": "https://www.youtube.com"},
            {"ex": "Behind Back Stop", "desc": "Sprint into behind-back halt.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Body Control"], "demo": "https://www.youtube.com"},
            {"ex": "Under Leg Stop", "desc": "Sprint into under-leg halt.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Balance"], "demo": "https://www.youtube.com"},
            {"ex": "Crossover-Spin", "desc": "Link cross and spin.", "base": 12, "unit": "reps", "rest": 45, "focus": ["Fluidity"], "demo": "https://www.youtube.com"},
            {"ex": "Boxer Shuffle Between", "desc": "Moving feet while going through.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Footwork"], "demo": "https://www.youtube.com"}
        ],
        "Softball": [
            {"ex": "Shuffle Step", "desc": "Instep to instep throw.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over Right Shoulder Tag"], "demo": "https://www.youtube.com"},
            {"ex": "Power Step", "desc": "Instep to ball; move around.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrap Around Tag"], "demo": "https://www.youtube.com"},
            {"ex": "Jam Step", "desc": "Backhand; glove foot steps.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Drop And Up"], "demo": "https://www.youtube.com"},
            {"ex": "Short Hop", "desc": "Make hops shorter.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Soft Hands"], "demo": "https://www.youtube.com"},
            {"ex": "Dart Throws", "desc": "Elbow, wrist, finger snap.", "base": 25, "unit": "reps", "rest": 30, "focus": ["Quick Release"], "demo": "https://www.youtube.com"},
            {"ex": "Tripod Grounders", "desc": "Bare hand down; eyes behind.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Eye Alignment"], "demo": "https://www.youtube.com"},
            {"ex": "Fence Work", "desc": "Feel fence; climb.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Spatial Awareness"], "demo": "https://www.youtube.com"},
            {"ex": "Do or Die", "desc": "Throw on run.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Momentum"], "demo": "https://www.youtube.com"},
            {"ex": "Glove Flip", "desc": "Using glove to flip ball.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Quick Transfer"], "demo": "https://www.youtube.com"},
            {"ex": "Backhand Flip", "desc": "Quick flick from backhand.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrist Snap"], "demo": "https://www.youtube.com"},
            {"ex": "Catcher Blocking", "desc": "Center of ball shift.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Body Angle"], "demo": "https://www.youtube.com"},
            {"ex": "Slide Dives", "desc": "Knees take you down.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Control"], "demo": "https://www.youtube.com"},
            {"ex": "Routine Fly Balls", "desc": "Catch back of ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Footing"], "demo": "https://www.youtube.com"},
            {"ex": "Pop-ups (Catcher)", "desc": "Standard tracking.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Vision"], "demo": "https://www.youtube.com"},
            {"ex": "3/4 Sway", "desc": "Bow & arrow tilt.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Core Strength"], "demo": "https://www.youtube.com"}
        ],
        "Track": [
            {"ex": "Leg Swings (F/S)", "desc": "Hip Joint Fluidity.", "base": 15, "unit": "reps", "rest": 15, "focus": ["Range of Motion"], "demo": "https://www.youtube.com"},
            {"ex": "Pogo Jumps", "desc": "Ankle Stiffness focus.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Elasticity"], "demo": "https://www.youtube.com"},
            {"ex": "A-March", "desc": "Posture & Dorsiflexion.", "base": 20, "unit": "m", "rest": 30, "focus": ["Toe Up"], "demo": "https://www.youtube.com"},
            {"ex": "B-Skips", "desc": "Hamstring 'Paw' Action.", "base": 30, "unit": "m", "rest": 45, "focus": ["Ground Contact"], "demo": "https://www.youtube.com"},
            {"ex": "Wall Drive Accels", "desc": "Drive Phase Mechanics.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Lean"], "demo": "https://www.youtube.com"},
            {"ex": "Flying 30s", "desc": "Pure Top-End Speed.", "base": 30, "unit": "m", "rest": 180, "focus": ["Top Speed"], "demo": "https://www.youtube.com"},
            {"ex": "Wicket Flys", "desc": "Max Velocity Maintenance.", "base": 40, "unit": "m", "rest": 120, "focus": ["Frequency"], "demo": "https://www.youtube.com"},
            {"ex": "Straight-Leg Bounds", "desc": "Glute/Hamstring Snap.", "base": 30, "unit": "m", "rest": 90, "focus": ["Active Foot"], "demo": "https://www.youtube.com"},
            {"ex": "Hill Sprints", "desc": "Force vs Gravity.", "base": 40, "unit": "m", "rest": 120, "focus": ["Knee Drive"], "demo": "https://www.youtube.com"},
            {"ex": "Tempo Strides", "desc": "Recovery & Form Work.", "base": 100, "unit": "m", "rest": 60, "focus": ["Technique"], "demo": "https://www.youtube.com"}
        ],
        "General": [
            {"ex": "Spiderman w/ Reach", "desc": "Hip & Thoracic mobility.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Opening Hips"], "demo": "https://www.youtube.com"},
            {"ex": "Bulgarian Split Squat", "desc": "Unilateral Strength.", "base": 10, "unit": "reps", "rest": 90, "focus": ["Knee Tracking"], "demo": "https://www.youtube.com"},
            {"ex": "Nordic Curls", "desc": "Eccentric Hamstring Safety.", "base": 8, "unit": "reps", "rest": 90, "focus": ["Slow Descent"], "demo": "https://www.youtube.com"},
            {"ex": "Pallof Press", "desc": "Anti-rotation core hold.", "base": 30, "unit": "sec", "rest": 30, "focus": ["Core Bracing"], "demo": "https://www.youtube.com"},
            {"ex": "Deadbugs", "desc": "Spinal Control.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Lower Back Flush"], "demo": "https://www.youtube.com"},
            {"ex": "Power Clean", "desc": "Rate of Force Development.", "base": 5, "unit": "reps", "rest": 120, "focus": ["Explosive Extension"], "demo": "https://www.youtube.com"},
            {"ex": "Box Jumps", "desc": "Vertical Displacement.", "base": 8, "unit": "reps", "rest": 60, "focus": ["Soft Landing"], "demo": "https://www.youtube.com"},
            {"ex": "Farmer Carries", "desc": "Grip & Core Anti-Flexion.", "base": 40, "unit": "m", "rest": 60, "focus": ["Posture"], "demo": "https://www.youtube.com"}
        ]
    }

# --- 3. SESSION LOGIC ---
vault = load_all_data()
target_count = 12 if sport_choice in ["Basketball", "Softball"] else 8

# Generate session if not exists or sport changed
if st.sidebar.button("🔄 Generate New Session"):
    st.session_state.current_session = random.sample(vault[sport_choice], min(len(vault[sport_choice]), target_count))

if st.session_state.current_session is None:
    st.session_state.current_session = random.sample(vault[sport_choice], min(len(vault[sport_choice]), target_count))

# --- 4. DISPLAY SESSION ---
st.title(f"{difficulty} {sport_choice} Session")
st.info(f"📍 Location: {location} | 📋 {target_count} Drills Loaded")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

for i, drill in enumerate(st.session_state.current_session):
    with st.container():
        st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            st.write(f"**Instructions:** {drill['desc']}")
            st.markdown("🎯 **Coach's Evaluation**")
            for focus_pt in drill["focus"]:
                st.checkbox(focus_pt, key=f"eval_{i}_{focus_pt}")
        
        with c2:
            st.metric("Target Goal", f"{int(drill['base'] * target_mult)} {drill['unit']}")
            if st.button("⏱️ START REST", key=f"rest_{i}"):
                ph = st.empty()
                for s in range(drill["rest"], -1, -1):
                    ph.metric("Recovery Time", f"{s}s")
                    time.sleep(1)
                ph.empty()
                st.success("Next Set!")

        with c3:
            st.markdown("🎥 **Action**")
            if st.button("Watch Demo", key=f"demo_{i}"):
                st.video(drill["demo"])
            st.file_uploader("Upload Progress", type=["mp4", "mov"], key=f"upload_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "location": location})
    st.balloons()
    st.success("Session saved to performance history!")
