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
if 'monthly_sessions' not in st.session_state:
    st.session_state.monthly_sessions = 0

# --- 2. DYNAMIC THEME & IPHONE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    field_label_color = "#7DF9FF"  # Electric Blue
    numeric_color = "#60A5FA"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    field_label_color = "#2563EB"  # Strong Blue
    numeric_color = "#000000"

btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    /* Universal Text Visibility */
    h1, h2, h3, p, span, li, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        font-weight: 700;
    }}

    /* BLUE TITLES: Target Set, Reps/Time, Completed */
    .stat-label, label[data-testid="stWidgetLabel"] p {{
        color: {field_label_color} !important;
        -webkit-text-fill-color: {field_label_color} !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }}

    /* Numeric & Input Colors */
    .stat-value, [data-testid="stNumericInput"] input {{
        color: {numeric_color} !important;
        -webkit-text-fill-color: {numeric_color} !important;
        font-weight: 900 !important;
        font-size: 20px !important;
    }}

    /* AGGRESSIVE BUTTON OVERRIDE: ALWAYS WHITE TEXT */
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

    /* Drill Header Styling */
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

# --- 3. MASTER DATABASE (9 DRILLS PER SPORT) ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at 3 heights.", "sets": 3, "base": 60, "unit": "sec", "rest": 30},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups for touch.", "sets": 4, "base": 20, "unit": "reps", "rest": 45},
            {"ex": "FIGURE 8", "desc": "Low handling through legs.", "sets": 3, "base": 45, "unit": "sec", "rest": 30},
            {"ex": "FREE THROWS", "desc": "Static routine practice.", "sets": 5, "base": 10, "unit": "makes", "rest": 60},
            {"ex": "V-DRIBBLE", "desc": "Explosive lateral control.", "sets": 3, "base": 50, "unit": "reps", "rest": 30},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral intensity.", "sets": 4, "base": 30, "unit": "sec", "rest": 45},
            {"ex": "BOX JUMPS", "desc": "Vertical power.", "sets": 3, "base": 12, "unit": "reps", "rest": 90},
            {"ex": "WALL SITS", "desc": "Isometric leg strength.", "sets": 3, "base": 60, "unit": "sec", "rest": 60},
            {"ex": "FULL COURT SPRINTS", "desc": "Conditioning finish.", "sets": 2, "base": 4, "unit": "laps", "rest": 120}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Quick ankle strikes.", "sets": 3, "base": 30, "unit": "m", "rest": 30},
            {"ex": "A-SKIPS", "desc": "Rhythmic knee drive.", "sets": 4, "base": 40, "unit": "m", "rest": 45},
            {"ex": "BOUNDING", "desc": "Horizontal power leaps.", "sets": 3, "base": 30, "unit": "m", "rest": 90},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical cycles.", "sets": 3, "base": 20, "unit": "sec", "rest": 30},
            {"ex": "ACCELERATIONS", "desc": "20m drive bursts.", "sets": 6, "base": 20, "unit": "m", "rest": 120},
            {"ex": "SINGLE LEG HOPS", "desc": "Ankle stability.", "sets": 3, "base": 10, "unit": "reps", "rest": 60},
            {"ex": "HILL SPRINTS", "desc": "Uphill force production.", "sets": 5, "base": 10, "unit": "sec", "rest": 90},
            {"ex": "RUSSIAN TWISTS", "desc": "Core rotation power.", "sets": 3, "base": 30, "unit": "reps", "rest": 30},
            {"ex": "COOL DOWN JOG", "desc": "Lactic acid flush.", "sets": 1, "base": 800, "unit": "m", "rest": 0}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Swing mechanics.", "sets": 4, "base": 25, "unit": "swings", "rest": 60},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid transfer speed.", "sets": 3, "base": 30, "unit": "reps", "rest": 30},
            {"ex": "FRONT TOSS", "desc": "Timing and direction.", "sets": 4, "base": 20, "unit": "swings", "rest": 60},
            {"ex": "LATERAL SHUFFLES", "desc": "Defensive range.", "sets": 3, "base": 30, "unit": "sec", "rest": 45},
            {"ex": "LONG TOSS", "desc": "Arm strength buildup.", "sets": 3, "base": 15, "unit": "throws", "rest": 60},
            {"ex": "WRIST SNAPS", "desc": "Forearm/Velocity focus.", "sets": 3, "base": 20, "unit": "reps", "rest": 30},
            {"ex": "SQUAT JUMPS", "desc": "Explosive leg drive.", "sets": 3, "base": 12, "unit": "reps", "rest": 60},
            {"ex": "SPRINT TO FIRST", "desc": "Base path speed.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45},
            {"ex": "BUNTING DRILLS", "desc": "Precision placement.", "sets": 3, "base": 10, "unit": "bunts", "rest": 30}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Leg power/Core tension.", "sets": 4, "base": 12, "unit": "reps", "rest": 90},
            {"ex": "PUSHUPS", "desc": "Chest/Tricep strength.", "sets": 3, "base": 15, "unit": "reps", "rest": 60},
            {"ex": "LUNGES", "desc": "Unilateral stability.", "sets": 3, "base": 10, "unit": "reps", "rest": 60},
            {"ex": "PLANK", "desc": "Total body isometric.", "sets": 3, "base": 45, "unit": "sec", "rest": 45},
            {"ex": "DUMBBELL ROW", "desc": "Back pull strength.", "sets": 4, "base": 12, "unit": "reps", "rest": 60},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "Dynamic core speed.", "sets": 3, "base": 30, "unit": "sec", "rest": 30},
            {"ex": "GLUTE BRIDGES", "desc": "Posterior engagement.", "sets": 3, "base": 15, "unit": "reps", "rest": 45},
            {"ex": "BURPEES", "desc": "Stamina/Intensity.", "sets": 3, "base": 10, "unit": "reps", "rest": 90},
            {"ex": "JUMP ROPE", "desc": "Footwork/Cardio.", "sets": 3, "base": 2, "unit": "min", "rest": 60}
        ]
    }
    return workouts.get(sport, [])

# --- 4. SIDEBAR NAVIGATION ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 0.8 if difficulty == "Elite" else 0.5

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:28px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

# --- 5. WORKOUT UI ---
st.title(f"{sport_choice} - {difficulty}")
drills = get_workout_template(sport_choice)

for i, item in enumerate(drills):
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-style: italic; opacity: 0.8;">{item["desc"]}</p>', unsafe_allow_html=True)
    
    # BLUE LABELS SECTION
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
        if st.button(f"FINISH DRILL ✅", key=f"done_{i}", use_container_width=True):
            st.toast(f"Drill {i+1} Logged!")
    with col_b:
        rest_time = int(item["rest"] * rest_mult)
        if st.button(f"REST {rest_time}s ⏱️", key=f"rest_{i}", use_container_width=True):
            ph = st.empty()
            for t in range(rest_time, -1, -1):
                ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                time.sleep(1)
            ph.empty()

    with st.expander("🎥 DEMO & UPLOAD"):
        st.file_uploader("Upload Session Clip", type=["mp4", "mov"], key=f"v_{i}")

st.divider()
if st.button("💾 SAVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.session_state.monthly_sessions += 1
    st.balloons()
    st.success("Session Saved to History!")
