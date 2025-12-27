import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & FEATURE INTEGRITY CHECK ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Check system to ensure features aren't lost during reruns
features = ["streak", "history", "selected_locs", "evals"]
for feature in features:
    if feature not in st.session_state:
        if feature == "streak": st.session_state.streak = 1
        if feature == "history": st.session_state.history = []
        if feature == "selected_locs": st.session_state.selected_locs = []
        if feature == "evals": st.session_state.evals = {}

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEME & ELECTRIC BLUE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue = "#00E5FF" 
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue = "#00B8D4" 

btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    h1, h2, h3, p, span, li, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        font-weight: 700;
    }}

    /* ELECTRIC BLUE LABELS */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        -webkit-text-fill-color: {electric_blue} !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }}

    /* HEADER STYLING */
    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header_bg}; border-left: 8px solid {accent};
        padding: 10px; border-radius: 0 10px 10px 0; margin-top: 25px;
    }}

    .sidebar-card {{ 
        padding: 12px; border-radius: 10px; border: 2px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. WORKOUT DATABASE (9 DRILLS PER SPORT) ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at 3 heights.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://youtube.com"},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups for touch.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "BOX JUMPS", "desc": "Explosive upward power.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": ""},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral intensity.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "FREE THROWS", "desc": "Muscle memory routine.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "V-DRIBBLE", "desc": "Wrist snap and control.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym", "demo": ""},
            {"ex": "WALL SITS", "desc": "Isometric leg strength.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "SPRINTS", "desc": "Full court conditioning.", "sets": 3, "base": 4, "unit": "laps", "rest": 90, "loc": "Gym", "demo": ""},
            {"ex": "MED BALL TWISTS", "desc": "Rotational power.", "sets": 3, "base": 20, "unit": "reps", "rest": 45, "loc": "Weight Room", "demo": ""}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Swing path precision.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": ""},
            {"ex": "TRANSFERS", "desc": "Glove to hand speed.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": ""},
            {"ex": "FRONT TOSS", "desc": "Timing and direction.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": ""},
            {"ex": "LATERAL SHUFFLES", "desc": "Defensive range.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Softball Field", "demo": ""},
            {"ex": "LONG TOSS", "desc": "Arm strength buildup.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "loc": "Softball Field", "demo": ""},
            {"ex": "WRIST SNAPS", "desc": "Ball rotation/velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": ""},
            {"ex": "SQUAT JUMPS", "desc": "Explosive leg drive.", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "SPRINT TO FIRST", "desc": "Explosive burst speed.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "loc": "Softball Field", "demo": ""},
            {"ex": "BUNTING", "desc": "Precision bat control.", "sets": 3, "base": 10, "unit": "bunts", "rest": 30, "loc": "Batting Cages", "demo": ""}
        ]
    }
    # Fallback to General Workout if sport not found
    all_drills = workouts.get(sport, [])
    return [d for d in all_drills if d['loc'] in locs]

# --- 4. SIDEBAR PANEL ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-card"><p style="margin:0; font-size:18px;">{get_now_est().strftime("%I:%M %p")}</p></div>', unsafe_allow_html=True)
    
    sport_choice = st.selectbox("Sport Select", ["Basketball", "Softball", "Track", "General Workout"])
    
    st.markdown("---")
    st.markdown("### 📍 LOCATION FILTER")
    loc_gym = st.checkbox("Gym", value=True)
    loc_track = st.checkbox("Track", value=True)
    loc_weight = st.checkbox("Weight Room", value=True)
    loc_cages = st.checkbox("Batting Cages", value=True)
    loc_field = st.checkbox("Softball Field", value=True)
    
    active_locs = []
    if loc_gym: active_locs.append("Gym")
    if loc_track: active_locs.append("Track")
    if loc_weight: active_locs.append("Weight Room")
    if loc_cages: active_locs.append("Batting Cages")
    if loc_field: active_locs.append("Softball Field")
    
    st.markdown("---")
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.markdown(f'<div class="sidebar-card"><p style="margin:0; font-size:22px;">{st.session_state.streak} DAY STREAK</p></div>', unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title("PRO-ATHLETE TRACKER")
drills = get_workout_template(sport_choice, active_locs)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if not drills:
    st.info("Adjust location filters in the sidebar to see your drills.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{item["ex"]} <small>({item["loc"]})</small></div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Target Set", value=str(item["sets"]), key=f"ts_{i}")
        with c2: 
            val = int(item["base"] * target_mult)
            st.text_input("Reps/Time", value=f"{val} {item['unit']}", key=f"rt_{i}")
        with c3: st.checkbox("Completed", key=f"f_{i}")
        
        st.text_area("Coaches Eval", placeholder="Notes on form/intensity...", key=f"eval_{i}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"LOG DRILL ✅", key=f"log_{i}", use_container_width=True):
                st.toast("Progress Saved")
        with col_b:
            rest_time = int(item["rest"] * rest_mult)
            if st.button(f"REST {rest_time}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_time, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:40px; color:{electric_blue};'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        with st.expander("🎥 DEMO & VIDEO UPLOAD"):
            if item["demo"]: st.markdown(f"[Watch Demo]({item['demo']})")
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"v_{i}")

# --- 6. WORKOUT SUMMARY SECTION ---
st.divider()
st.markdown(f"### 📊 WORKOUT SUMMARY")
if st.button("GENERATE SUMMARY", use_container_width=True):
    summary_data = []
    for i, item in enumerate(drills):
        status = "✅" if st.session_state.get(f"f_{i}") else "❌"
        summary_data.append({
            "Drill": item["ex"],
            "Location": item["loc"],
            "Status": status,
            "Evaluation": st.session_state.get(f"eval_{i}", "")
        })
    df = pd.DataFrame(summary_data)
    st.table(df)

if st.button("💾 SAVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Session Archived!")
