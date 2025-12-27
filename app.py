import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME LOGIC ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    """Returns current time in US/Eastern (EST/EDT)."""
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 1

# --- 2. THEME & ELECTRIC BLUE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue = "#7DF9FF" 
    numeric_color = "#60A5FA"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue = "#00E5FF" 
    numeric_color = "#000000"

btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    h1, h2, h3, p, span, li, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        font-weight: 700;
    }}

    /* ELECTRIC BLUE TITLES */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        -webkit-text-fill-color: {electric_blue} !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
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
        font-weight: 800 !important;
        font-size: 16px !important;
    }}

    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header_bg}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 30px;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. WORKOUT DATABASE (9 DRILLS PER SPORT WITH LOCATION TAGS) ---
def get_workout_template(sport, locations):
    # Mapping drills to specific locations for filtering
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym"},
            {"ex": "MIKAN SERIES", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym"},
            {"ex": "FIGURE 8", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "loc": "Gym"},
            {"ex": "FREE THROWS", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym"},
            {"ex": "V-DRIBBLE", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym"},
            {"ex": "DEFENSIVE SLIDES", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym"},
            {"ex": "BOX JUMPS", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room"},
            {"ex": "WALL SITS", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room"},
            {"ex": "FULL COURT SPRINTS", "sets": 2, "base": 4, "unit": "laps", "rest": 120, "loc": "Gym"}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "sets": 3, "base": 30, "unit": "m", "rest": 30, "loc": "Track"},
            {"ex": "A-SKIPS", "sets": 4, "base": 40, "unit": "m", "rest": 45, "loc": "Track"},
            {"ex": "BOUNDING", "sets": 3, "base": 30, "unit": "m", "rest": 90, "loc": "Track"},
            {"ex": "HIGH KNEES", "sets": 3, "base": 20, "unit": "sec", "rest": 30, "loc": "Track"},
            {"ex": "ACCELERATIONS", "sets": 6, "base": 20, "unit": "m", "rest": 120, "loc": "Track"},
            {"ex": "SINGLE LEG HOPS", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Track"},
            {"ex": "HILL SPRINTS", "sets": 5, "base": 10, "unit": "sec", "rest": 90, "loc": "Track"},
            {"ex": "RUSSIAN TWISTS", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Weight Room"},
            {"ex": "800M FINISHER", "sets": 1, "base": 800, "unit": "m", "rest": 180, "loc": "Track"}
        ],
        "Softball": [
            {"ex": "TEE WORK", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Gym"},
            {"ex": "GLOVE TRANSFERS", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Gym"},
            {"ex": "FRONT TOSS", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "loc": "Gym"},
            {"ex": "LATERAL SHUFFLES", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym"},
            {"ex": "LONG TOSS", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "loc": "Track"},
            {"ex": "WRIST SNAPS", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Gym"},
            {"ex": "SQUAT JUMPS", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room"},
            {"ex": "SPRINT TO FIRST", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "loc": "Track"},
            {"ex": "BUNTING DRILLS", "sets": 3, "base": 10, "unit": "bunts", "rest": 30, "loc": "Gym"}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room"},
            {"ex": "PUSHUPS", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "loc": "Gym"},
            {"ex": "LUNGES", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Gym"},
            {"ex": "PLANK", "sets": 3, "base": 45, "unit": "sec", "rest": 45, "loc": "Gym"},
            {"ex": "DUMBBELL ROW", "sets": 4, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room"},
            {"ex": "MOUNTAIN CLIMBERS", "sets": 3, "base": 30, "unit": "sec", "rest": 30, "loc": "Gym"},
            {"ex": "GLUTE BRIDGES", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "loc": "Gym"},
            {"ex": "BURPEES", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "loc": "Gym"},
            {"ex": "JUMP ROPE", "sets": 3, "base": 2, "unit": "min", "rest": 60, "loc": "Gym"}
        ]
    }
    
    all_drills = workouts.get(sport, [])
    # Filter based on selected locations. If no location selected, show all.
    if not locations:
        return all_drills
    return [d for d in all_drills if d['loc'] in locations]

# --- 4. SIDEBAR ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])

# NEW: LOCATION SELECTOR
location_choices = st.sidebar.multiselect(
    "Location Filter", 
    options=["Gym", "Track", "Weight Room"],
    default=["Gym", "Track", "Weight Room"],
    help="Select one or multiple locations to see drills for those areas."
)

difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")

# Multipliers
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:28px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title(f"{sport_choice} Session")
drills = get_workout_template(sport_choice, location_choices)

if not drills:
    st.warning("No drills found for the selected location(s). Please check your filters in the sidebar.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]} ({item["loc"]})</div>', unsafe_allow_html=True)
        
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
                st.toast(f"Drill {i+1} Saved!")
        with col_b:
            rest_time = int(item["rest"] * rest_mult)
            if st.button(f"REST {rest_time}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_time, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        with st.expander("🎥 SESSION VIDEO"):
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"v_{i}")

    st.divider()
    if st.button("💾 SAVE COMPLETE SESSION", use_container_width=True):
        st.session_state.streak += 1
        st.balloons()
        st.success("Full Session Archived!")
