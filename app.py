import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'streak' not in st.session_state:
    st.session_state.streak = 1

# --- 2. DYNAMIC THEME & ELECTRIC BLUE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue = "#7DF9FF" 
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue = "#00E5FF" 

btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    h1, h2, h3, p, span, li, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        font-weight: 700;
    }}

    /* ELECTRIC BLUE TITLES (Target Set, Reps/Time, Completed) */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        -webkit-text-fill-color: {electric_blue} !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }}

    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        border-radius: 12px !important;
    }}

    div.stButton > button p, div.stButton > button span {{
        color: {btn_txt_white} !important;
        -webkit-text-fill-color: {btn_txt_white} !important;
        font-weight: 800;
    }}

    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header_bg}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 30px;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. WORKOUT DATABASE (9 DRILLS PER SPORT WITH DESCRIPTIONS) ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at 3 heights.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://youtube.com/placeholder1"},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups for touch and rhythm.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://youtube.com/placeholder2"},
            {"ex": "FIGURE 8", "desc": "Low, tight handling through legs.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://youtube.com/placeholder3"},
            {"ex": "FREE THROWS", "desc": "Static routine practice for muscle memory.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym", "demo": "https://youtube.com/placeholder4"},
            {"ex": "V-DRIBBLE", "desc": "Explosive lateral control and wrist snap.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym", "demo": "https://youtube.com/placeholder5"},
            {"ex": "DEFENSIVE SLIDES", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "desc": "Lateral intensity drill.", "demo": ""},
            {"ex": "BOX JUMPS", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "desc": "Vertical power development.", "demo": ""},
            {"ex": "WALL SITS", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room", "desc": "Isometric leg strength.", "demo": ""},
            {"ex": "FULL COURT SPRINTS", "sets": 2, "base": 4, "unit": "laps", "rest": 120, "loc": "Gym", "desc": "Conditioning finish.", "demo": ""}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Quick ankle strikes with low knee drive.", "sets": 3, "base": 30, "unit": "m", "rest": 30, "loc": "Track", "demo": ""},
            {"ex": "A-SKIPS", "desc": "Rhythmic knee drive and arm synchronization.", "sets": 4, "base": 40, "unit": "m", "rest": 45, "loc": "Track", "demo": ""},
            {"ex": "BOUNDING", "desc": "Horizontal power leaps focusing on air time.", "sets": 3, "base": 30, "unit": "m", "rest": 90, "loc": "Track", "demo": ""},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical cycles and foot speed.", "sets": 3, "base": 20, "unit": "sec", "rest": 30, "loc": "Track", "demo": ""},
            {"ex": "ACCELERATIONS", "desc": "20m drive bursts from a crouched start.", "sets": 6, "base": 20, "unit": "m", "rest": 120, "loc": "Track", "demo": ""},
            {"ex": "SINGLE LEG HOPS", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Track", "desc": "Ankle stability.", "demo": ""},
            {"ex": "HILL SPRINTS", "sets": 5, "base": 10, "unit": "sec", "rest": 90, "loc": "Track", "desc": "Uphill force production.", "demo": ""},
            {"ex": "RUSSIAN TWISTS", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Weight Room", "desc": "Core rotation power.", "demo": ""},
            {"ex": "800M FINISHER", "sets": 1, "base": 800, "unit": "m", "rest": 180, "loc": "Track", "desc": "Lactic acid threshold test.", "demo": ""}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Swing mechanics and point of contact.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Softball Cages", "demo": ""},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid transfer from glove to hand.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": ""},
            {"ex": "FRONT TOSS", "desc": "Timing and directional hitting.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "loc": "Softball Cages", "demo": ""},
            {"ex": "LATERAL SHUFFLES", "desc": "Defensive range and low center of gravity.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Softball Field", "demo": ""},
            {"ex": "LONG TOSS", "desc": "Arm strength buildup and accuracy.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "loc": "Softball Field", "demo": ""},
            {"ex": "WRIST SNAPS", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Softball Field", "desc": "Forearm velocity.", "demo": ""},
            {"ex": "SQUAT JUMPS", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "desc": "Explosive leg drive.", "demo": ""},
            {"ex": "SPRINT TO FIRST", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "loc": "Softball Field", "desc": "Base path speed.", "demo": ""},
            {"ex": "BUNTING DRILLS", "sets": 3, "base": 10, "unit": "bunts", "rest": 30, "loc": "Softball Cages", "desc": "Precision placement.", "demo": ""}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Leg power with core tension.", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": ""},
            {"ex": "PUSHUPS", "desc": "Chest and tricep strength.", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "LUNGES", "desc": "Unilateral stability and balance.", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "PLANK", "desc": "Total body isometric core strength.", "sets": 3, "base": 45, "unit": "sec", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "DUMBBELL ROW", "desc": "Back pull strength and posture.", "sets": 4, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "MOUNTAIN CLIMBERS", "sets": 3, "base": 30, "unit": "sec", "rest": 30, "loc": "Gym", "desc": "Dynamic core speed.", "demo": ""},
            {"ex": "GLUTE BRIDGES", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "loc": "Gym", "desc": "Posterior engagement.", "demo": ""},
            {"ex": "BURPEES", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "loc": "Gym", "desc": "Full body intensity.", "demo": ""},
            {"ex": "JUMP ROPE", "sets": 3, "base": 2, "unit": "min", "rest": 60, "loc": "Gym", "desc": "Footwork and cardio.", "demo": ""}
        ]
    }
    all_drills = workouts.get(sport, [])
    return [d for d in all_drills if d['loc'] in locs]

# --- 4. SIDEBAR PANEL ---
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-card">
        <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">TIME (EST)</p>
        <p style="margin:0; font-size:20px; font-weight:900;">{get_now_est().strftime('%I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

    sport_choice = st.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])

    st.markdown("---")
    st.markdown("### 📍 LOCATION CHECKBOXES")
    l1 = st.checkbox("Gym", value=True)
    l2 = st.checkbox("Track", value=True)
    l3 = st.checkbox("Weight Room", value=True)
    l4 = st.checkbox("Softball Cages", value=(sport_choice == "Softball"))
    l5 = st.checkbox("Softball Field", value=(sport_choice == "Softball"))

    active_locs = []
    if l1: active_locs.append("Gym")
    if l2: active_locs.append("Track")
    if l3: active_locs.append("Weight Room")
    if l4: active_locs.append("Softball Cages")
    if l5: active_locs.append("Softball Field")

    st.markdown("---")
    difficulty = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.markdown(f"""
    <div class="sidebar-card">
        <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
        <p style="margin:0; font-size:28px; font-weight:900;">{st.session_state.streak} DAYS</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title(f"{sport_choice} Session")
drills = get_workout_template(sport_choice, active_locs)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if not drills:
    st.warning("No drills selected. Please check location boxes in the side panel.")
else:
    for i, item in enumerate(drills):
        # Drill Title and Location
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]} <span style="font-size:12px; opacity:0.6;">({item["loc"]})</span></div>', unsafe_allow_html=True)
        
        # RESTORED: Drill Description
        st.markdown(f'<p style="font-style: italic; font-weight: 500; margin-top: 5px;">{item["desc"]}</p>', unsafe_allow_html=True)
        
        # Electric Blue Inputs
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("Target Set", value=str(item["sets"]), key=f"ts_{i}")
        with c2:
            val = int(item["base"] * target_mult)
            st.text_input("Reps/Time", value=f"{val} {item['unit']}", key=f"rt_{i}")
        with c3:
            st.checkbox("Completed", key=f"f_{i}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"LOG DRILL ✅", key=f"done_{i}", use_container_width=True):
                st.toast("Logged!")
        with col_b:
            rest_time = int(item["rest"] * rest_mult)
            if st.button(f"REST {rest_time}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_time, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        # RESTORED: Demo Video and Clip Upload
        with st.expander("🎥 DEMO & UPLOAD"):
            if item["demo"]:
                st.markdown(f"[Watch Demo Video]({item['demo']})")
            else:
                st.write("No demo video available.")
            st.file_uploader("Upload Session Clip", type=["mp4", "mov"], key=f"v_{i}")

st.divider()
if st.button("💾 SAVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Session saved!")
