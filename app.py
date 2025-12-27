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

    /* ELECTRIC BLUE TITLES: Target Set, Reps/Time, Completed */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        -webkit-text-fill-color: {electric_blue} !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Global Button Style: Forced White Text */
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

# --- 3. WORKOUT DATABASE (9 DRILLS PER SPORT) ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at 3 heights: knees, waist, and shoulders.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://youtube.com/watch?v=basketball_pound"},
            {"ex": "MIKAN SERIES", "desc": "Continuous alternating layups to develop touch around the rim.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://youtube.com/watch?v=mikan_drill"},
            {"ex": "FIGURE 8", "desc": "Keep the ball low and tight while moving through the legs.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "loc": "Gym", "demo": ""},
            {"ex": "FREE THROWS", "desc": "Deep breaths, consistent routine. Focus on the back of the rim.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "V-DRIBBLE", "desc": "Aggressive side-to-side dribbling to improve lateral control.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym", "demo": ""},
            {"ex": "DEFENSIVE SLIDES", "desc": "Stay low, chest up, and do not cross your feet.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "BOX JUMPS", "desc": "Explosive upward movement. Land softly on the box.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": ""},
            {"ex": "WALL SITS", "desc": "Hold a 90-degree angle. Keep back flat against the wall.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "FULL COURT SPRINTS", "desc": "Finish with max effort. Baseline to baseline.", "sets": 2, "base": 4, "unit": "laps", "rest": 120, "loc": "Gym", "demo": ""}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Rapid, low foot strikes focusing on dorsiflexion.", "sets": 3, "base": 30, "unit": "m", "rest": 30, "loc": "Track", "demo": ""},
            {"ex": "A-SKIPS", "desc": "Rhythmic skipping with high knees and aggressive arm drive.", "sets": 4, "base": 40, "unit": "m", "rest": 45, "loc": "Track", "demo": ""},
            {"ex": "BOUNDING", "desc": "Maximize horizontal distance and air time per stride.", "sets": 3, "base": 30, "unit": "m", "rest": 90, "loc": "Track", "demo": ""},
            {"ex": "HIGH KNEES", "desc": "Max reps in place or moving. Maintain upright posture.", "sets": 3, "base": 20, "unit": "sec", "rest": 30, "loc": "Track", "demo": ""},
            {"ex": "ACCELERATIONS", "desc": "Drive out for 20m. Focus on the 'piston' leg action.", "sets": 6, "base": 20, "unit": "m", "rest": 120, "loc": "Track", "demo": ""},
            {"ex": "SINGLE LEG HOPS", "desc": "Develop ankle stability and reactive power.", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Track", "demo": ""},
            {"ex": "HILL SPRINTS", "desc": "Short, high-intensity bursts up a steep incline.", "sets": 5, "base": 10, "unit": "sec", "rest": 90, "loc": "Track", "demo": ""},
            {"ex": "RUSSIAN TWISTS", "desc": "Core rotation with weighted implement or medicine ball.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Weight Room", "demo": ""},
            {"ex": "800M FINISHER", "desc": "Endurance-based sprint to test lactic threshold.", "sets": 1, "base": 800, "unit": "m", "rest": 180, "loc": "Track", "demo": ""}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Focus on hand path and driving through the center of the ball.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Softball Cages", "demo": ""},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid transfer from glove to hand. Focus on quick release.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": ""},
            {"ex": "FRONT TOSS", "desc": "Hit to all fields. Maintain balance throughout the swing.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "loc": "Softball Cages", "demo": ""},
            {"ex": "LATERAL SHUFFLES", "desc": "Stay low in a squat position. Quick, explosive steps.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Softball Field", "demo": ""},
            {"ex": "LONG TOSS", "desc": "Gradually increase distance. Use crow-hop for power.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "loc": "Softball Field", "demo": ""},
            {"ex": "WRIST SNAPS", "desc": "Isolated wrist movement to improve ball spin and velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": ""},
            {"ex": "SQUAT JUMPS", "desc": "Full squat into explosive vertical jump.", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "SPRINT TO FIRST", "desc": "Burst out of the box and run through the bag.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "loc": "Softball Field", "demo": ""},
            {"ex": "BUNTING DRILLS", "desc": "Deadening the ball. Focus on angle of the bat.", "sets": 3, "base": 10, "unit": "bunts", "rest": 30, "loc": "Softball Cages", "demo": ""}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Hold weight at chest. Drive knees out and chest up.", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": ""},
            {"ex": "PUSHUPS", "desc": "Full range of motion. Chest to floor, elbows at 45 degrees.", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "LUNGES", "desc": "Alternate legs. Keep front knee behind toes.", "sets": 3, "base": 10, "unit": "reps", "rest": 60, "loc": "Gym", "demo": ""},
            {"ex": "PLANK", "desc": "Squeeze glutes and core. Maintain straight line.", "sets": 3, "base": 45, "unit": "sec", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "DUMBBELL ROW", "desc": "Pull weight to hip. Focus on squeezing the shoulder blade.", "sets": 4, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "demo": ""},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "Drive knees to chest while maintaining a high plank.", "sets": 3, "base": 30, "unit": "sec", "rest": 30, "loc": "Gym", "demo": ""},
            {"ex": "GLUTE BRIDGES", "desc": "Drive through heels. Squeeze glutes at the top.", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "loc": "Gym", "demo": ""},
            {"ex": "BURPEES", "desc": "Chest to floor, explosive jump at the top.", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "loc": "Gym", "demo": ""},
            {"ex": "JUMP ROPE", "desc": "Light on feet. Use wrists to turn the rope.", "sets": 3, "base": 2, "unit": "min", "rest": 60, "loc": "Gym", "demo": ""}
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
st.title(f"{sport_choice} - Training Session")
drills = get_workout_template(sport_choice, active_locs)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if not drills:
    st.warning("Please check the location boxes in the side panel to see your drills.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]} <span style="font-size:12px; opacity:0.6;">({item["loc"]})</span></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-style: italic; font-weight: 500; margin-bottom: 0px; margin-top: 5px;">{item["desc"]}</p>', unsafe_allow_html=True)
        
        # Grid for Electric Blue Field Titles
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

        with st.expander("🎥 DEMO & UPLOAD"):
            if item["demo"]:
                st.markdown(f"[Watch Demo Video]({item['demo']})")
            else:
                st.write("No demo video link provided.")
            st.file_uploader("Upload Session Clip", type=["mp4", "mov"], key=f"v_{i}")

st.divider()
if st.button("💾 SAVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Training session archived successfully!")
