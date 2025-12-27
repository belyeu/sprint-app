import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. High-Visibility Theme Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Initialize Session State
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'session_saved' not in st.session_state: 
    st.session_state.session_saved = False
if 'monthly_sessions' not in st.session_state:
    st.session_state.monthly_sessions = 0

# Sidebar Toggle for Dark Mode
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors
if dark_mode:
    bg_color = "#0F172A"
    text_color = "#FFFFFF"
    accent_color = "#00FFFF"  # ELECTRIC BLUE
    header_bg = "#334155"
    sidebar_bg = "#1E293B"
    sidebar_text = "#FFFFFF"
    input_bg = "#1E293B" 
    sport_text_color = "#000000" 
    numeric_color = "#00FFFF"    # Electric Blue in Dark Mode
else:
    bg_color = "#F8FAFC"
    text_color = "#0F172A"
    accent_color = "#00FFFF"  # ELECTRIC BLUE
    header_bg = "#E2E8F0"
    sidebar_bg = "#FFFFFF"
    sidebar_text = "#0F172A"
    input_bg = "#FFFFFF"
    sport_text_color = "#FFFFFF" 
    numeric_color = "#000000"    # FORCED BLACK FOR IPHONE/LIGHT MODE
    
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; }}
    .main .block-container {{ padding-left: 5rem; padding-right: 2rem; background-color: {bg_color}; }}
    
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
        color: {sidebar_text} !important;
        -webkit-text-fill-color: {sidebar_text} !important;
    }}

    div[data-baseweb="select"] span {{
        color: {sport_text_color} !important;
        -webkit-text-fill-color: {sport_text_color} !important;
    }}

    /* --- IPHONE NUMERIC INPUT FIX --- */
    /* Targets inputs, number fields, and the big stat values */
    input, 
    textarea, 
    [data-testid="stNumericInput"] input,
    .stat-value, 
    [role="slider"], 
    [data-testid="stMarkdownContainer"] p > span {{
        color: {numeric_color} !important;
        -webkit-text-fill-color: {numeric_color} !important;
        opacity: 1 !important; /* Fixes iPhone's forced light gray on disabled or specific inputs */
        font-weight: 900 !important;
    }}

    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 2px solid {accent_color} !important;
    }}

    .stat-label {{ font-size: 14px !important; font-weight: 800 !important; color: {accent_color} !important; text-transform: uppercase; }}
    .stat-value {{ font-size: 32px !important; margin-bottom: 5px; }}

    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent_color} !important;
        text-transform: uppercase; margin-top: 30px; border-left: 10px solid {accent_color};
        padding: 10px 15px; background-color: {header_bg}; border-radius: 0 10px 10px 0;
    }}
    
    .timer-text {{
        font-size: 60px !important; font-weight: bold !important; color: {accent_color} !important;
        text-align: center; font-family: 'Courier New', monospace; border: 4px solid {accent_color}; padding: 10px;
    }}

    .stButton>button {{ 
        background-color: {accent_color} !important; color: black !important; 
        border-radius: 10px !important; font-weight: 800 !important; 
        width: 100%; height: 55px !important;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; 
        border: 2px solid {accent_color}; background-color: {sidebar_bg};
    }}
    
    div[data-testid="stProgress"] > div > div > div > div {{
        background-color: {accent_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Sidebar ---
now = datetime.now()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">SESSION START</p>
    <p style="margin:0; font-size:16px; font-weight:700;">{now.strftime("%B %d, %Y")}</p>
    <p style="margin:0; font-size:24px; font-weight:900; color:{numeric_color} !important;">{now.strftime("%I:%M %p")}</p>
</div>
""", unsafe_allow_html=True)

goal = 20
progress = min(st.session_state.monthly_sessions / goal, 1.0)
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">{now.strftime("%B").upper()} GOAL</p>
    <p style="font-size:28px; font-weight:900; margin:0; color:{numeric_color} !important;">{st.session_state.monthly_sessions} / {goal}</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.progress(progress)

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">STREAK</p>
    <p style="font-size:32px; font-weight:900; margin:0; color:{numeric_color} !important;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 3. Master Database ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Eyes Up"]},
            {"ex": "MIKAN SERIES", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["Soft Touch", "High Finish"]},
            {"ex": "FIGURE 8", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Ball Control", "Quick Hands"]},
            {"ex": "FREE THROWS", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "vid": "https://www.youtube.com/watch?v=R4-fR8_mXAc", "eval": ["Routine", "Follow Through"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "sets": 3, "base": 30, "unit": "meters", "rest": 30, "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Quiet Hips"]},
            {"ex": "A-SKIPS", "sets": 4, "base": 40, "unit": "meters", "rest": 45, "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Drive"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact"]},
            {"ex": "GLOVE TRANSFERS", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Clean Pull", "Fast Grip"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up"]},
            {"ex": "PUSHUPS", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout"]}
        ]
    }
    return workouts.get(sport, [])

# --- 4. Main App UI ---
st.markdown(f"<h1>{sport_choice} Session</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

for i in range(len(drills)):
    item = drills[i]
    drill_key = f"{sport_choice}_{i}"
    
    if drill_key not in st.session_state: 
        st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<p class="stat-label">Target Sets</p><p class="stat-value">{item["sets"]}</p>', unsafe_allow_html=True)
    with c2:
        reps_val = int(item['base'] * target_mult)
        st.markdown(f'<p class="stat-label">Reps/Time</p><p class="stat-value">{reps_val} {item["unit"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="stat-label">Completed</p><p class="stat-value">{st.session_state[drill_key]}</p>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"DONE ✅", key=f"done_{i}"):
            st.session_state[drill_key] += 1
            st.rerun()
    with col_b:
        if st.button(f"REST ⏱️", key=f"rest_{i}"):
            final_rest = int(item['rest'] * rest_mult)
            ph = st.empty()
            for t in range(final_rest, -1, -1):
                ph.markdown(f'<p class="timer-text">{t//60:02d}:{t%60:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state[drill_key] += 1
            st.rerun()

    st.markdown("### 📋 COACH'S EVALUATION")
    eval_cols = st.columns(2)
    for idx in range(len(item['eval'])):
        criteria = item['eval'][idx]
        eval_cols[idx % 2].checkbox(criteria, key=f"ev_{drill_key}_{idx}")
    
    st.select_slider(f"Intensity (RPE)", options=range(1, 11), value=8, key=f"rpe_{drill_key}")
    st.text_input("Notes", key=f"note_{drill_key}")

    with st.expander("🎥 DEMO & UPLOAD"):
        st.video(item['vid'])
        st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"up_{i}")

st.divider()
if st.button("💾 SAVE WORKOUT"):
    st.balloons()
    st.session_state.streak += 1
    st.session_state.monthly_sessions += 1
    st.session_state.session_saved = True
    st.rerun()

# --- 5. Post-Workout Analytics ---
if st.session_state.session_saved:
    st.success("Session saved!")
    summary_data = []
    for i in range(len(drills)):
        drill_key = f"{sport_choice}_{i}"
        summary_data.append({"Drill": drills[i]["ex"], "Completed": st.session_state.get(drill_key, 0)})
    
    df = pd.DataFrame(summary_data)
    st.bar_chart(df, x="Drill", y="Completed", color=accent_color)
