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
    st.session_state.streak = 0

# --- 2. DYNAMIC THEME & IPHONE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    # High-contrast Light Mode: Text is Pure Black (#000000)
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

# Button label color is ALWAYS white
btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{ background-color: {bg} !important; }}
    
    /* 1. Force Body Text to Black (Light Mode) or White (Dark Mode) */
    h1, h2, h3, p, span, li, label, .stMarkdown p {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
        font-weight: 600;
    }}

    /* 2. AGGRESSIVE BUTTON OVERRIDE: Text is ALWAYS White */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        border-radius: 12px !important;
    }}

    /* Targets all possible text containers inside buttons */
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

    /* 3. Expander & Form Input Styling */
    [data-testid="stExpander"], input, textarea {{
        background-color: {header} !important;
        border: 2px solid {accent} !important;
        border-radius: 10px !important;
        color: {text} !important;
    }}

    /* Drill Header Styling */
    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent}; 
        background-color: {header}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER DATABASE (8 DRILLS PER SPORT) ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Stationary power dribbling (Waist/Knee/Ankle).", "rest": 30},
            {"ex": "MIKAN SERIES", "desc": "Continuous layups under rim alternating hands.", "rest": 45},
            {"ex": "FIGURE 8", "desc": "Low ball handling through and around legs.", "rest": 30},
            {"ex": "V-DRIBBLE", "desc": "Front and side explosive V-shaped dribbles.", "rest": 30},
            {"ex": "WALL SITS", "desc": "Isometric leg strength and core engagement.", "rest": 60},
            {"ex": "BOX JUMPS", "desc": "Max vertical explosion with soft landing.", "rest": 90},
            {"ex": "FREE THROWS", "desc": "Focus on ritual, breathing, and follow-through.", "rest": 60},
            {"ex": "DEFENSIVE SLIDES", "desc": "Low-hip lateral movement across the key.", "rest": 45}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Small steps focusing on active ankles.", "rest": 30},
            {"ex": "A-SKIPS", "desc": "Rhythmic skips with aggressive knee drive.", "rest": 45},
            {"ex": "BOUNDING", "desc": "Max horizontal distance per jump.", "rest": 90},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical cycles, staying on midfoot.", "rest": 30},
            {"ex": "20M ACCELERATIONS", "desc": "Full effort drive phase from a 3-point start.", "rest": 120},
            {"ex": "SINGLE LEG HOPS", "desc": "Unilateral power and ankle stability.", "rest": 60},
            {"ex": "HILL SPRINTS", "desc": "Short uphill bursts for explosive strength.", "rest": 90},
            {"ex": "CORE ROTATION", "desc": "Russian twists or seated med-ball cycles.", "rest": 30}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Hard contact focus through the middle.", "rest": 60},
            {"ex": "GLOVE TRANSFERS", "desc": "Quick hands from catch to throwing grip.", "rest": 30},
            {"ex": "FRONT TOSS", "desc": "Timing drills with directional hitting.", "rest": 60},
            {"ex": "LATERAL SHUFFLES", "desc": "Quick-step fielding range drills.", "rest": 45},
            {"ex": "LONG TOSS", "desc": "Building arm strength and throwing arc.", "rest": 60},
            {"ex": "WRIST SNAPS", "desc": "Isolated flick for ball spin and velocity.", "rest": 30},
            {"ex": "SQUAT JUMPS", "desc": "Explosive power for base path speed.", "rest": 60},
            {"ex": "SPRINT TO FIRST", "desc": "Home-to-first max speed rounding.", "rest": 45}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Full depth squats with upright chest.", "rest": 90},
            {"ex": "PUSHUPS", "desc": "Military style, chest to floor.", "rest": 60},
            {"ex": "LUNGES", "desc": "Alternating steps with 90-degree angles.", "rest": 60},
            {"ex": "PLANK", "desc": "Forearm hold with glute/core tension.", "rest": 45},
            {"ex": "DUMBBELL ROW", "desc": "Controlled pull focusing on lats.", "rest": 60},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "Rapid knee-to-chest dynamic core.", "rest": 30},
            {"ex": "GLUTE BRIDGES", "desc": "High squeeze for posterior chain power.", "rest": 45},
            {"ex": "BURPEES", "desc": "Full body explosive conditioning.", "rest": 90}
        ]
    }
    return workouts.get(sport, [])

# --- 4. SIDEBAR NAVIGATION & STATS ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    <p style="margin:0; font-size:13px;">{now_est.strftime('%A, %b %d')}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "Session History"])
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])

# --- 5. WORKOUT PLAN PAGE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} Session")
    drills = get_workout_template(sport_choice)

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"DONE ✅", key=f"d_{i}", use_container_width=True):
                st.toast(f"Logged: {item['ex']}")
        with c2:
            if st.button(f"REST ⏱️", key=f"r_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        st.checkbox("Perfect Form", key=f"f_{i}")
        st.text_input("Notes", key=f"n_{i}", placeholder="Set details...")
        
        with st.expander("🎥 VIDEO LOG"):
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"u_{i}")

    st.divider()
    s1, s2 = st.columns(2)
    with s1:
        if st.button("💾 SAVE WORKOUT", use_container_width=True):
            timestamp = get_now_est().strftime("%b %d, %I:%M %p")
            st.session_state.history.append({"date": timestamp, "sport": sport_choice})
            st.session_state.streak += 1
            st.balloons()
            st.success(f"Saved at {timestamp} EST")
    with s2:
        if st.button("🔄 RESET", use_container_width=True):
            st.rerun()

# --- 6. SESSION HISTORY PAGE ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No saved sessions yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:12px; border:1px solid {accent}; background-color:{header}; margin-bottom:12px;">
                <p style="margin:0; font-weight:900; font-size:18px; color:{accent} !important;">{log['sport']} Session</p>
                <p style="margin:0; font-size:14px; font-weight:700;">{log['date']} EST</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("Clear History"):
            st.session_state.history = []
            st.rerun()
