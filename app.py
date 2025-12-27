import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME LOGIC ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    """Returns current time in US/Eastern (EST/EDT) regardless of server location."""
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0

# --- 2. DYNAMIC THEME & IPHONE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    # High-contrast Light Mode: Pure Black text for visibility on iPhone
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

# Force button text to white
btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    /* Global App Background */
    .stApp {{ background-color: {bg} !important; }}
    
    /* 1. Universal Text Visibility (Black in Light / White in Dark) */
    h1, h2, h3, p, span, li, label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
        font-weight: 700;
    }}

    /* 2. AGGRESSIVE BUTTON OVERRIDE: ALWAYS WHITE TEXT */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        border-radius: 12px !important;
    }}

    /* Force all text inside buttons to Pure White */
    div.stButton > button p, 
    div.stButton > button span, 
    div.stButton > button div, 
    div.stButton > button label {{
        color: {btn_txt_white} !important;
        -webkit-text-fill-color: {btn_txt_white} !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        opacity: 1 !important;
        text-transform: uppercase;
    }}

    /* 3. Expander & Input Box Styling */
    [data-testid="stExpander"], input, textarea {{
        background-color: {header_bg} !important;
        border: 2px solid {accent} !important;
        border-radius: 10px !important;
        color: {text} !important;
    }}

    /* Drill Header Styling */
    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header_bg}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
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
            {"ex": "POUND SERIES", "desc": "Power dribbling at waist, knee, and ankle heights.", "rest": 40},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups focusing on touch and footwork.", "rest": 40},
            {"ex": "FIGURE 8", "desc": "Low-to-ground ball handling through and around legs.", "rest": 30},
            {"ex": "V-DRIBBLE", "desc": "Explosive lateral control with a heavy pound.", "rest": 30},
            {"ex": "WALL SITS", "desc": "Isometric leg strength hold for core stability.", "rest": 60},
            {"ex": "BOX JUMPS", "desc": "Max vertical explosion with controlled landings.", "rest": 90},
            {"ex": "FREE THROWS", "desc": "Focus on ritual, breath, and high release.", "rest": 60},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral quickness and active hands across the key.", "rest": 45},
            {"ex": "FULL COURT SPRINTS", "desc": "End-to-end conditioning at 100% effort.", "rest": 120}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Small steps focusing on active foot strikes.", "rest": 30},
            {"ex": "A-SKIPS", "desc": "Rhythmic knee drive and aggressive mid-foot strike.", "rest": 45},
            {"ex": "BOUNDING", "desc": "Max horizontal distance per jump stride.", "rest": 90},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical cycles while staying upright.", "rest": 30},
            {"ex": "20M ACCELERATIONS", "desc": "Full effort drive phase bursts from a 3-point start.", "rest": 120},
            {"ex": "SINGLE LEG HOPS", "desc": "Unilateral stability and force production.", "rest": 60},
            {"ex": "HILL SPRINTS", "desc": "Max effort uphill bursts for explosive power.", "rest": 90},
            {"ex": "RUSSIAN TWISTS", "desc": "Seated core rotation with explosive movement.", "rest": 30},
            {"ex": "COOL DOWN FLUSH", "desc": "Low-intensity jog to clear lactic acid.", "rest": 60}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Focus on driving through the center of the ball.", "rest": 60},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid hands from catch to throwing position.", "rest": 30},
            {"ex": "FRONT TOSS", "desc": "Timing drills with directional hitting focus.", "rest": 60},
            {"ex": "LATERAL SHUFFLES", "desc": "Quick-step fielding range movement.", "rest": 45},
            {"ex": "LONG TOSS", "desc": "Building arm strength and throwing arc.", "rest": 60},
            {"ex": "WRIST SNAPS", "desc": "Isolated flick for velocity and ball spin.", "rest": 30},
            {"ex": "SQUAT JUMPS", "desc": "Explosive power for base path acceleration.", "rest": 60},
            {"ex": "SPRINT TO FIRST", "desc": "Max speed turn at the bag.", "rest": 45},
            {"ex": "BUNTING CONTROL", "desc": "Sacrifice and drag bunt placement.", "rest": 40}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Weighted depth squats with upright chest.", "rest": 90},
            {"ex": "PUSHUPS", "desc": "Military style, chest to floor with core locked.", "rest": 60},
            {"ex": "LUNGES", "desc": "Alternating steps with 90-degree stability.", "rest": 60},
            {"ex": "PLANK", "desc": "Static forearm hold with total body tension.", "rest": 45},
            {"ex": "DUMBBELL ROW", "desc": "Back strength and shoulder health focus.", "rest": 60},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "Rapid dynamic core and conditioning.", "rest": 30},
            {"ex": "GLUTE BRIDGES", "desc": "Posterior chain engagement and power.", "rest": 45},
            {"ex": "BURPEES", "desc": "Full body explosive intensity.", "rest": 90},
            {"ex": "JUMP ROPE", "desc": "Footwork speed and sustained cardio.", "rest": 45}
        ]
    }
    return workouts.get(sport, [])

# --- 4. SIDEBAR CONTROLS ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    <p style="margin:0; font-size:13px;">{now_est.strftime('%A, %b %d')}</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "Session History"])
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])

# LEVEL TOGGLE
level = st.sidebar.select_slider("Training Level", options=["Standard", "Elite", "Pro"])
rest_multiplier = {"Standard": 1.0, "Elite": 0.75, "Pro": 0.5}[level]

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

# --- 5. WORKOUT PLAN PAGE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} - {level}")
    drills = get_workout_template(sport_choice)

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        current_rest = int(item["rest"] * rest_multiplier)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"DONE ✅", key=f"d_{i}", use_container_width=True):
                st.toast(f"Completed: {item['ex']}")
        with c2:
            if st.button(f"REST {current_rest}s ⏱️", key=f"r_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(current_rest, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        st.checkbox("Perfect Execution", key=f"f_{i}")
        st.text_input("Performance Notes", key=f"n_{i}", placeholder="Log details...")

    st.divider()
    s1, s2 = st.columns(2)
    with s1:
        if st.button("💾 SAVE WORKOUT", use_container_width=True):
            timestamp = get_now_est().strftime("%b %d, %I:%M %p")
            st.session_state.history.append({"date": timestamp, "sport": sport_choice, "level": level})
            st.session_state.streak += 1
            st.balloons()
            st.success(f"Saved at {timestamp} EST")
    with s2:
        if st.button("🔄 RESET SESSION", use_container_width=True):
            st.rerun()

# --- 6. HISTORY PAGE ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No saved sessions yet. Time to get to work!")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:12px; border:1px solid {accent}; background-color:{header_bg}; margin-bottom:12px;">
                <p style="margin:0; font-weight:900; font-size:18px; color:{accent} !important;">{log['sport']} ({log['level']})</p>
                <p style="margin:0; font-size:14px; font-weight:700;">{log['date']} EST</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("Clear History"):
            st.session_state.history = []
            st.rerun()
