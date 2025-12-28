import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
import random

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []

# Sidebar Theme & Location
st.sidebar.markdown("### 🏟️ SESSION SETTINGS")
location = st.sidebar.selectbox("Current Location", ["Softball Field", "Batting Cages", "Track", "Weight Room", "Gym"])
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}
h1, h2, h3, p, span, label, li {{ color: {text} !important; font-weight: 500; }}
.drill-header {{
    font-size: 18px !important; font-weight: 800 !important;
    color: {accent} !important; background-color: {header}; 
    border-left: 6px solid {accent}; padding: 8px; margin-top: 15px; border-radius: 0 5px 5px 0;
}}
.stButton>button {{ background-color: {accent} !important; color: white !important; font-weight: 700; width: 100%; }}
</style>
""", unsafe_allow_html=True)

# --- 2. THE COMPLETE DATA VAULT ---
# Note: In a production app, these would be in a separate .py or .json file
def get_full_databases():
    return {
        "Basketball": [
            {"ex": "High/Low Walking (R/L)", "desc": "3 High, 3 Low; walking forward.", "base": 20, "unit": "m", "rest": 30, "focus": ["Rhythm", "Control"]},
            {"ex": "High/Low Backpedal (R/L)", "desc": "3 High, 3 Low; backpedaling.", "base": 20, "unit": "m", "rest": 30, "focus": ["Balance"]},
            {"ex": "Iverson Cross", "desc": "Wide deceptive step-across.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Deception", "Wide Step"]},
            {"ex": "Shammgod", "desc": "Push out R, pull back L.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Extension", "Speed"]},
            {"ex": "Pocket Pulls", "desc": "Pull ball to hip pocket while maintaining dribble.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Security", "Wrist Snap"]},
            {"ex": "Cross Step Jab", "desc": "Jab at defense while crossing.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Sharp Cut"]},
            {"ex": "Trae Young Pullback", "desc": "Lunge forward and snap back.", "base": 12, "unit": "reps", "rest": 40, "focus": ["Deceleration"]},
            {"ex": "Double Tap", "desc": "Drop and tap twice before crossing.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Quick Hands"]},
            {"ex": "V-Dribble", "desc": "One-handed 'V' shape in front.", "base": 50, "unit": "reps", "rest": 30, "focus": ["Pound Speed"]},
            {"ex": "Stationary High Crossover", "desc": "Dribble height at chest.", "base": 30, "unit": "reps", "rest": 30, "focus": ["Power"]},
            {"ex": "Spin to Post", "desc": "Drive R, spin to turn back to basket.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Footwork"]},
            {"ex": "Stutter Step", "desc": "Chop feet to freeze defender.", "base": 20, "unit": "m", "rest": 30, "focus": ["Frequency"]},
            {"ex": "Behind Back Float", "desc": "Letting ball hang in hand while moving.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Pace"]},
            {"ex": "Inside Out Jab", "desc": "Fake move with heavy foot jab.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Deception"]},
            {"ex": "Retreat Inside Out", "desc": "Create space, then fake/attack.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Space Creation"]}
        ],
        "Softball": [
            {"ex": "Shuffle Step", "desc": "Instep to instep; point toward throw.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over right shoulder tag"]},
            {"ex": "Instep Kick", "desc": "Kick throwing foot instep over glove.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over left shoulder tag"]},
            {"ex": "Power Step", "desc": "Instep to ball; move around ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrap around tag"]},
            {"ex": "Jam Step", "desc": "Backhand; glove foot steps with ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Drop And Up"]},
            {"ex": "Dart Throws", "desc": "Elbow, wrist, finger snap (no legs).", "base": 25, "unit": "reps", "rest": 30, "focus": ["Over right shoulder tag"]},
            {"ex": "Short Hop", "desc": "Straight/Fore/Back; make hops shorter.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Soft Hands"]},
            {"ex": "Tripod Grounders", "desc": "Bare hand down; eyes behind glove.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Eye Level"]},
            {"ex": "Fence Work", "desc": "Feel fence with bare hand; climb.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Spatial Awareness"]},
            {"ex": "Do or Die", "desc": "Throw on run; glove/throwing foot forward.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Momentum"]},
            {"ex": "Glove Flip", "desc": "Using glove to flip ball.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Quick Release"]},
            {"ex": "3/4 Sway", "desc": "Bow & arrow with lower body tilt.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Core Tilt"]},
            {"ex": "Backhand Flip", "desc": "Quick flick from backhand side.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrist Snap"]},
            {"ex": "Catcher Blocking", "desc": "Shifting body to center of ball.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Angling Ball"]},
            {"ex": "Slide Dives", "desc": "Knees take you down for low ball.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Body Control"]},
            {"ex": "Routine Fly Balls", "desc": "Glove foot forward; catch back of ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Catch Position"]}
        ],
        "Track": [
            {"ex": "Leg Swings (F/S)", "desc": "Hip Joint Fluidity.", "base": 15, "unit": "reps", "rest": 15, "focus": ["Range of Motion"]},
            {"ex": "Pogo Jumps", "desc": "Ankle Stiffness focus.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Elasticity"]},
            {"ex": "A-March", "desc": "Posture & Dorsiflexion.", "base": 20, "unit": "m", "rest": 30, "focus": ["Toe Up"]},
            {"ex": "B-Skips", "desc": "Hamstring 'Paw' Action.", "base": 30, "unit": "m", "rest": 45, "focus": ["Ground Contact"]},
            {"ex": "Wall Drive Accels", "desc": "Drive Phase Mechanics.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Body Angle"]},
            {"ex": "Flying 30s", "desc": "Pure Top-End Speed.", "base": 30, "unit": "m", "rest": 180, "focus": ["Relaxed Face"]},
            {"ex": "Wicket Flys", "desc": "Max Velocity Maintenance.", "base": 40, "unit": "m", "rest": 120, "focus": ["Step Frequency"]},
            {"ex": "Straight-Leg Bounds", "desc": "Glute/Hamstring Snap.", "base": 30, "unit": "m", "rest": 90, "focus": ["Active Foot"]},
            {"ex": "Hill Sprints", "desc": "Explosive Force against gravity.", "base": 40, "unit": "m", "rest": 120, "focus": ["Knee Drive"]},
            {"ex": "Tempo Strides", "desc": "Recovery & Form Work.", "base": 100, "unit": "m", "rest": 60, "focus": ["Technique"]}
        ],
        "General": [
            {"ex": "Spiderman w/ Reach", "desc": "Hip & Thoracic mobility.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Opening Hips"]},
            {"ex": "Bulgarian Split Squat", "desc": "Unilateral Strength.", "base": 10, "unit": "reps", "rest": 90, "focus": ["Knee Tracking"]},
            {"ex": "Nordic Curls", "desc": "Eccentric Hamstring Safety.", "base": 8, "unit": "reps", "rest": 90, "focus": ["Slow Descent"]},
            {"ex": "Pallof Press", "desc": "Anti-rotation core hold.", "base": 30, "unit": "sec", "rest": 30, "focus": ["Core Bracing"]},
            {"ex": "Deadbugs", "desc": "Spinal Control.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Lower Back Flush"]},
            {"ex": "Power Clean", "desc": "Rate of Force Development.", "base": 5, "unit": "reps", "rest": 120, "focus": ["Explosive Extension"]},
            {"ex": "Box Jumps", "desc": "Vertical Displacement.", "base": 8, "unit": "reps", "rest": 60, "focus": ["Soft Landing"]},
            {"ex": "Farmer Carries", "desc": "Grip & Core Anti-Flexion.", "base": 40, "unit": "m", "rest": 60, "focus": ["Shoulder Stability"]},
            {"ex": "Russian Twists", "desc": "Rotational Power.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Controlled Rotation"]},
            {"ex": "Burpees", "desc": "Conditioning & Power.", "base": 15, "unit": "reps", "rest": 60, "focus": ["Cardio Output"]}
        ]
    }

# --- 3. LOGIC FOR SESSION GENERATION ---
sport_choice = st.sidebar.selectbox("Select Database", ["Basketball", "Softball", "Track", "General"])
difficulty = st.sidebar.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")

all_data = get_full_databases()[sport_choice]

# Enforce exercise counts
count = 12 if sport_choice in ["Basketball", "Softball"] else 8
session_drills = random.sample(all_data, min(len(all_data), count))

# --- 4. MAIN UI ---
st.title(f"🔥 {difficulty} {sport_choice} Session")
st.caption(f"Location: {location} | Goal: {count} Exercises")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

for i, drill in enumerate(session_drills):
    with st.container():
        st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.write(f"**Action:** {drill['desc']}")
            # Focus points as Coach Eval checkboxes
            st.markdown("🎯 **Coach's Eval**")
            for f in drill["focus"]:
                st.checkbox(f, key=f"eval_{sport_choice}_{i}_{f}")
        
        with c2:
            st.metric("Target", f"{int(drill['base'] * target_mult)} {drill['unit']}")
            if st.button("⏱️ REST", key=f"rest_{i}"):
                ph = st.empty()
                for s in range(drill["rest"], -1, -1):
                    ph.metric("Timer", f"{s}s")
                    time.sleep(1)
                ph.empty()

        with c3:
            st.markdown("🎥 **Evidence**")
            st.button("View Demo", key=f"demo_{i}") # Placeholder for video link
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"clip_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "location": location})
    st.balloons()
    st.success(f"Session saved! Current Streak: {len(st.session_state.history)} sessions.")
