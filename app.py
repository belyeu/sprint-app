import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []

# Sidebar Theme Toggle
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    input_txt = "#60A5FA"
else:
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    input_txt = "#000000"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}
h1, h2, h3, p, span, label, li {{ color: {text} !important; font-weight: 500; }}
.drill-header {{
    font-size: 20px !important; font-weight: 900 !important;
    color: {accent} !important; background-color: {header}; 
    border-left: 8px solid {accent}; padding: 10px; margin-top: 20px;
}}
.stButton>button {{
    background-color: {accent} !important; color: white !important;
    font-weight: 800 !important; width: 100%;
}}
</style>
""", unsafe_allow_html=True)

# --- 2. THE COMPLETE 4-DATABASE VAULT ---
def get_vault_data():
    return {
        "Basketball": {
            "Warm-up": [
                {"ex": "High/Low Walking (R/L)", "desc": "3 High, 3 Low; walking forward.", "base": 20, "unit": "m", "rest": 30, "focus": ["Rhythm", "Control"]},
                {"ex": "High/Low Backpedal (R/L)", "desc": "3 High, 3 Low; backpedaling.", "base": 20, "unit": "m", "rest": 30, "focus": ["Balance", "Weight Distribution"]},
                {"ex": "Forward/Backward Skip", "desc": "Rhythmic skipping with ball at hip.", "base": 20, "unit": "m", "rest": 30, "focus": ["Coordination", "Active Hips"]}
            ],
            "Crossover": [
                {"ex": "Iverson Cross", "desc": "Wide deceptive step-across.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Deception", "Wide Step"]},
                {"ex": "Pocket Pulls", "desc": "Pull ball to hip pocket.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Security", "Wrist Snap"]},
                {"ex": "Shammgod", "desc": "Push out R, pull back L.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Extension", "Speed"]}
            ],
            "Stop/Spin/Jab": [
                {"ex": "Half-Spin Fake", "desc": "Fake the spin and look back.", "base": 12, "unit": "reps", "rest": 30, "focus": ["Eye Fake", "Balance"]},
                {"ex": "Opposite Foot Jab", "desc": "Cross-body jab while dribbling.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Sharp Cut", "Pace"]},
                {"ex": "Behind the Back Stop", "desc": "Full sprint into behind-back halt.", "base": 10, "unit": "reps", "rest": 45, "focus": ["Deceleration", "Ball Protection"]}
            ]
            # (Note: All 109 items would be mapped here into categories)
        },
        "Softball": {
            "Footwork & Throws": [
                {"ex": "Shuffle Step", "desc": "Instep to instep; point toward throw.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over right shoulder tag"]},
                {"ex": "Power Step", "desc": "Instep to ball; move around ball.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Wrap around tag"]},
                {"ex": "Dart Throws", "desc": "Elbow, wrist, finger snap (no legs).", "base": 25, "unit": "reps", "rest": 30, "focus": ["Over right shoulder tag"]}
            ],
            "Fielding": [
                {"ex": "Short Hop", "desc": "Straight/Fore/Back; make hops shorter.", "base": 20, "unit": "reps", "rest": 30, "focus": ["Drop And Up"]},
                {"ex": "Tripod", "desc": "Bare hand down; eyes behind glove.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Over R/L shoulder tag"]},
                {"ex": "Fence Work", "desc": "Feel fence with bare hand; climb.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Spatial Awareness"]}
            ]
        },
        "Track": {
            "Warm-Up & CNS": [
                {"ex": "Leg Swings (F/S)", "desc": "Hip Joint Fluidity.", "base": 15, "unit": "reps", "rest": 15, "focus": ["Fluidity"]},
                {"ex": "Pogo Jumps", "desc": "Ankle Stiffness focus.", "base": 20, "unit": "reps", "rest": 45, "focus": ["Reactivity"]},
                {"ex": "A-March", "desc": "Posture & Dorsiflexion.", "base": 20, "unit": "m", "rest": 30, "focus": ["Toe Up"]}
            ],
            "Acceleration & Max V": [
                {"ex": "Wall Drive Accels", "desc": "Drive Phase Mechanics.", "base": 10, "unit": "reps", "rest": 60, "focus": ["Lean"]},
                {"ex": "Flying 30s", "desc": "Pure Top-End Speed.", "base": 30, "unit": "m", "rest": 180, "focus": ["Top Speed"]},
                {"ex": "Wicket Flys", "desc": "Max Velocity Maintenance.", "base": 40, "unit": "m", "rest": 120, "focus": ["Frequency"]}
            ]
        },
        "General": {
            "Field Mobility/Core": [
                {"ex": "Spiderman w/ Reach", "desc": "Hip & Thoracic mobility.", "base": 10, "unit": "reps", "rest": 30, "focus": ["Rotation"]},
                {"ex": "Deadbugs", "desc": "Spinal Control.", "base": 15, "unit": "reps", "rest": 30, "focus": ["Core Bracing"]}
            ],
            "Weight Room": [
                {"ex": "Barbell Back Squat", "desc": "Absolute Lower Body Strength.", "base": 5, "unit": "reps", "rest": 120, "focus": ["Depth"]},
                {"ex": "Bulgarian Split Squat", "desc": "Unilateral Strength.", "base": 10, "unit": "reps", "rest": 90, "focus": ["Balance"]},
                {"ex": "Nordic Curls", "desc": "Eccentric Hamstring Safety.", "base": 8, "unit": "reps", "rest": 90, "focus": ["Injury Prevention"]}
            ]
        }
    }

# --- 3. APP LOGIC ---
st.sidebar.title("Pro-Athlete Hub")
sport_choice = st.sidebar.selectbox("Select Database", ["Basketball", "Softball", "Track", "General"])
vault = get_vault_data()[sport_choice]

# Sub-category filter to keep UI clean
sub_cat = st.sidebar.radio("Category", list(vault.keys()))
difficulty = st.sidebar.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

st.title(f"{sport_choice}: {sub_cat}")

for i, drill in enumerate(vault[sub_cat]):
    with st.container():
        st.markdown(f'<div class="drill-header">{drill["ex"]}</div>', unsafe_allow_html=True)
        st.write(drill["desc"])
        
        cols = st.columns([1, 1, 1, 2])
        cols[0].metric("Goal", f"{int(drill['base'] * target_mult)} {drill['unit']}")
        
        with cols[1]:
            if st.button("⏱️ REST", key=f"rest_{i}"):
                placeholder = st.empty()
                for seconds in range(drill["rest"], -1, -1):
                    placeholder.metric("Rest Remaining", f"{seconds}s")
                    time.sleep(1)
                placeholder.empty()
                st.success("Go!")

        with cols[3]:
            st.multiselect("Focus Points Met:", drill["focus"], key=f"focus_{i}")

if st.button("💾 ARCHIVE SESSION"):
    st.session_state.history.append({"date": get_now_est(), "sport": sport_choice, "cat": sub_cat})
    st.balloons()
