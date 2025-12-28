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

# Initialize Session States
if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None
if 'active_sport' not in st.session_state: st.session_state.active_sport = ""

# --- 2. SIDEBAR (RESTORED) ---
with st.sidebar:
    st.header("🏟️ SESSION CONTROL")
    location = st.selectbox("Location", ["Gym", "Softball Field", "Batting Cages", "Track", "Weight Room"])
    sport_choice = st.selectbox("Sport Database", ["Basketball", "Softball", "Track", "General"])
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    dark_mode = st.toggle("Dark Mode", value=True)
    
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = None # Force refresh

# Custom CSS for UI
if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}
h1, h2, h3, p, span, label, li {{ color: {text} !important; }}
.drill-header {{
    font-size: 20px !important; font-weight: 800 !important;
    color: {accent} !important; background-color: {header}; 
    border-left: 8px solid {accent}; padding: 12px; margin-top: 20px; border-radius: 4px;
}}
</style>
""", unsafe_allow_html=True)

# --- 3. RAW DATABASES ---
def get_vault():
    return {
        "Basketball": [
            {"ex": "High/Low Walking (R/L)", "desc": "3 High, 3 Low; walking forward.", "base": 20, "unit": "m", "rest": 30, "focus": ["Rhythm", "Wrist Snap", "Eye Level"]},
            {"ex": "Iverson Cross", "desc": "Wide deceptive step-across.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Width", "Deception", "Low Hips"]},
            {"ex": "Shammgod", "desc": "Push out R, pull back L.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Extension", "Change of Pace"]},
            {"ex": "Pocket Pulls", "desc": "Pull ball to hip pocket.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Security", "Control"]},
            {"ex": "Trae Young Pullback", "desc": "Lunge forward and snap back.", "base": 12, "unit": "reps", "rest": 40, "focus": ["Deceleration", "Balance"]},
            {"ex": "Spin to Post", "desc": "Drive R, spin to turn back.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Pivot Accuracy"]},
            {"ex": "Double Tap", "desc": "Drop and tap twice before cross.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Hand Speed"]},
            {"ex": "V-Dribble (R/L)", "desc": "One-handed 'V' shape.", "base": 50, "unit": "reps", "rest": 30, "focus": ["Pound Force"]},
            {"ex": "Stutter Step", "desc": "Chop feet to freeze defender.", "base": 20, "unit": "m", "rest": 30, "focus": ["Foot Frequency"]},
            {"ex": "Inside Out Jab", "desc": "Fake move with heavy jab.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Head Fake"]},
            {"ex": "Retreat Inside Out", "desc": "Create space, then fake.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Space Creation"]},
            {"ex": "Behind Back Stop", "desc": "Sprint into behind-back halt.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Body Control"]},
            {"ex": "Under Leg Stop", "desc": "Sprint into under-leg halt.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Balance"]},
            {"ex": "Crossover-Spin", "desc": "Link cross and spin.", "base": 12, "unit": "reps", "rest": 45, "focus": ["Fluidity"]},
            {"ex": "Boxer Shuffle Between", "desc": "Moving feet while going through.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Footwork"]}
        ],
        "Softball": [
            {"ex": "Shuffle Step", "desc": "Instep to instep throw.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over Right Shoulder Tag"]},
            {"ex": "Power Step", "desc": "Instep to ball; move around.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrap Around Tag"]},
            {"ex": "Jam Step", "desc": "Backhand; glove foot steps.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Drop And Up"]},
            {"ex": "Short Hop", "desc": "Make hops shorter.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Soft Hands"]},
            {"ex": "Dart Throws", "desc": "Elbow, wrist, finger snap.", "base": 25, "unit": "reps", "rest": 30, "focus": ["Quick Release"]},
            {"ex": "Tripod Grounders", "desc": "Bare hand down; eyes behind.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Eye Alignment"]},
            {"ex": "Fence Work", "desc": "Feel fence; climb.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Spatial Awareness"]},
            {"ex": "Do or Die", "desc": "Throw on run.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Momentum"]},
            {"ex": "Glove Flip", "desc": "Using glove to flip ball.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Quick Transfer"]},
            {"ex": "Backhand Flip", "desc": "Quick flick from backhand.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrist Snap"]},
            {"ex": "Catcher Blocking", "desc": "Center of ball shift.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Body Angle"]},
            {"ex": "Slide Dives", "desc": "Knees take you down.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Control"]},
            {"ex": "Routine Fly Balls", "desc": "Catch back of ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Footing"]},
            {"ex": "Pop-ups (Catcher)", "desc": "Standard tracking.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Vision"]},
            {"ex": "3/4 Sway", "desc": "Bow & arrow tilt.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Core Strength"]}
        ],
        "Track": [
            {"ex": "Leg Swings (F/S)", "desc": "Hip Joint Fluidity.", "base": 15, "unit": "reps", "rest": 15, "focus": ["Range of Motion"]},
            {"ex": "Pogo Jumps", "desc": "Ankle Stiffness focus.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Elasticity"]},
            {"ex": "A-March", "desc": "Posture & Dorsiflexion.", "base": 20, "unit": "m", "rest": 30, "focus": ["Toe Up"]},
            {"ex": "B-Skips", "desc": "Hamstring 'Paw' Action.", "base": 30, "unit": "m", "rest": 45, "focus": ["Ground Contact"]},
            {"ex": "Wall Drive Accels", "desc": "Drive Phase Mechanics.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Lean"]},
            {"ex": "Flying 30s", "desc": "Pure Top-End Speed.", "base": 30, "unit": "m", "rest": 180, "focus": ["Top Speed"]},
            {"ex": "Wicket Flys", "desc": "Max Velocity Maintenance.", "base": 40, "unit": "m", "rest": 120, "focus": ["Frequency"]},
            {"ex": "Straight-Leg Bounds", "desc": "Glute/Hamstring Snap.", "base": 30, "unit": "m", "rest": 90, "focus": ["Active Foot"]},
            {"ex": "Hill Sprints", "desc": "Force vs Gravity.", "base": 40, "unit": "m", "rest": 120, "focus": ["Knee Drive"]},
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
            {"ex": "Farmer Carries", "desc": "Grip & Core Anti-Flexion.", "base": 40, "unit": "m", "rest": 60, "focus": ["Posture"]}
        ]
    }

# --- 4. SESSION GENERATION ---
vault = get_vault()
count_needed = 12 if sport_choice in ["Basketball", "Softball"] else 8

# Refresh session if sport changes or requested
if st.session_state.active_sport != sport_choice or st.session_state.current_session is None:
    st.session_state.current_session = random.sample(vault[sport_choice], min(len(vault[sport_choice]), count_needed))
    st.session_state.active_sport = sport_choice

# --- 5. MAIN DISPLAY ---
st.title(f"🔥 {difficulty} {sport_choice} Training")
st.subheader(f"📍 {location} | {get_now_est().strftime('%b %d, %I:%M %p')}")

mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

for i, drill in enumerate(st.session_state.current_session):
    st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**Instruction:** {drill['desc']}")
        st.markdown("✅ **Coach's Evaluation (Focus Points)**")
        for point in drill["focus"]:
            st.checkbox(point, key=f"eval_{i}_{point}_{sport_choice}")
            
    with col2:
        st.metric("Goal", f"{int(drill['base'] * mult)} {drill['unit']}")
        if st.button("⏱️ START REST", key=f"timer_{i}"):
            timer_box = st.empty()
            for s in range(drill["rest"], -1, -1):
                timer_box.metric("Rest Remaining", f"{s}s")
                time.sleep(1)
            timer_box.empty()
            st.success("Set Complete!")

    with col3:
        st.markdown("🎥 **Evidence**")
        st.button("Watch Demo Video", key=f"vid_{i}")
        st.file_uploader("Upload Progress Clip", type=["mp4", "mov"], key=f"up_{i}")

st.divider()
if st.button("💾 ARCHIVE SESSION", use_container_width=True):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "loc": location})
    st.balloons()
    st.success("Session saved to Athlete History!")
