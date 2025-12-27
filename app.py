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

# Sidebar Toggle for Dark Mode
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors based on Mode
if dark_mode:
    bg_color = "#0F172A"; text_color = "#FFFFFF"; accent_color = "#38BDF8"
    header_bg = "#334155"; sidebar_bg = "#1E293B"; sidebar_text = "#FFFFFF"
    input_bg = "#334155"; input_text = "#FFFFFF"
else:
    bg_color = "#F8FAFC"; text_color = "#0F172A"; accent_color = "#2563EB"
    header_bg = "#E2E8F0"; sidebar_bg = "#FFFFFF"; sidebar_text = "#0F172A"
    input_bg = "#FFFFFF"; input_text = "#0F172A"

st.markdown(f"""
    <style>
    /* Prevent sidebar overlap on main content */
    .main .block-container {{
        padding-left: 5rem;
        padding-right: 2rem;
    }}

    /* Main Background */
    .main {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    /* SIDEBAR & DROPDOWN VISIBILITY FIX (iPhone & Laptop) */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: {sidebar_text} !important;
        opacity: 1 !important;
    }}

    /* Specific fix for Selectbox/Dropdown visibility */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {accent_color} !important;
    }}
    
    /* Ensure dropdown list items are visible */
    ul[role="listbox"] li {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}

    /* Drill Headers */
    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent_color} !important;
        text-transform: uppercase; margin-top: 30px; border-left: 10px solid {accent_color};
        padding: 10px 15px; background-color: {header_bg}; border-radius: 0 10px 10px 0;
    }}
    
    .stat-label {{ font-size: 13px !important; font-weight: 800 !important; color: {accent_color} !important; text-transform: uppercase; }}
    .stat-value {{ font-size: 28px !important; font-weight: 900 !important; color: {text_color} !important; margin-bottom: 5px; }}
    
    /* Timer Display */
    .timer-text {{
        font-size: 60px !important; font-weight: bold !important; color: {accent_color} !important;
        text-align: center; font-family: 'Courier New', monospace; background: {bg_color};
        border-radius: 12px; border: 4px solid {accent_color}; padding: 10px; margin: 10px 0;
    }}

    /* Button Styling */
    .stButton>button {{ 
        background-color: {accent_color} !important; color: white !important; 
        border-radius: 10px !important; font-weight: 800 !important; 
        width: 100%; height: 55px !important; font-size: 16px !important;
        border: none !important;
    }}

    .sidebar-card {{ padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 2px solid {accent_color}; }}

    /* Responsive adjustments for mobile */
    @media (max-width: 768px) {{
        .main .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .drill-header {{ font-size: 20px !important; }}
        .stat-value {{ font-size: 24px !important; }}
        .timer-text {{ font-size: 50px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Drill Database (8 Exercises Per Sport) ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "sets": 3, "base": 60, "inc": 10, "unit": "sec", "rest": 30, "type": "cond", "desc": "Power dribbles.", "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Eyes Up"]},
            {"ex": "MIKAN SERIES", "sets": 4, "base": 20, "inc": 2, "unit": "reps", "rest": 45, "type": "power", "desc": "Alternating layups.", "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["Soft Touch", "High Finish"]},
            {"ex": "FIGURE 8", "sets": 3, "base": 45, "inc": 5, "unit": "sec", "rest": 30, "type": "cond", "desc": "Low dribbles around legs.", "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Ball Control", "Quick Hands"]},
            {"ex": "FREE THROWS", "sets": 5, "base": 10, "inc": 2, "unit": "makes", "rest": 60, "type": "skill", "desc": "Concentration shots.", "vid": "https://www.youtube.com/watch?v=R4-fR8_mXAc", "eval": ["Routine", "Follow Through"]},
            {"ex": "DEFENSIVE SLIDES", "sets": 4, "base": 30, "inc": 5, "unit": "sec", "rest": 45, "type": "cond", "desc": "Lateral quickness.", "vid": "https://www.youtube.com/watch?v=pAnVmqk-G9I", "eval": ["Low Hips", "No Crossing Feet"]},
            {"ex": "BOX JUMPS", "sets": 3, "base": 10, "inc": 2, "unit": "reps", "rest": 90, "type": "power", "desc": "Explosive vertical.", "vid": "https://www.youtube.com/watch?v=52r6I-z6r-I", "eval": ["Soft Landing", "Full Extension"]},
            {"ex": "V-DRIBBLE", "sets": 3, "base": 40, "inc": 5, "unit": "reps", "rest": 30, "type": "skill", "desc": "In-and-out dribbles.", "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "eval": ["Wide Dribble", "Rhythm"]},
            {"ex": "WALL SITS", "sets": 3, "base": 45, "inc": 10, "unit": "sec", "rest": 60, "type": "cond", "desc": "Leg endurance.", "vid": "https://www.youtube.com/watch?v=y-wV4Venusw", "eval": ["90 Degree Angle", "Back Flat"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "sets": 4, "base": 12, "inc": 2, "unit": "reps", "rest": 90, "type": "power", "desc": "Hold weight at chest.", "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up"]},
            {"ex": "PUSHUPS", "sets": 3, "base": 15, "inc": 3, "unit": "reps", "rest": 60, "type": "power", "desc": "Full range of motion.", "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout"]},
            {"ex": "LUNGES", "sets": 3, "base": 10, "inc": 2, "unit": "reps/leg", "rest": 60, "type": "power", "desc": "Step forward.", "vid": "https://www.youtube.com/watch?v=L8fvypPrzzs", "eval": ["Balance", "Upright Torso"]},
            {"ex": "PLANK", "sets": 3, "base": 45, "inc": 10, "unit": "sec", "rest": 45, "type": "cond", "desc": "Core hold.", "vid": "https://www.youtube.com/watch?v=pSHjTRCQxIw", "eval": ["Flat Back", "Glutes Engaged"]},
            {"ex": "DUMBBELL ROW", "sets": 4, "base": 12, "inc": 1, "unit": "reps", "rest": 60, "type": "power", "desc": "Pull to hip.", "vid": "https://www.youtube.com/watch?v=6KA7SFr8P4E", "eval": ["Elbow High", "No Rotation"]},
            {"ex": "MOUNTAIN CLIMBERS", "sets": 3, "base": 30, "inc": 5, "unit": "sec", "rest": 30, "type": "cond", "desc": "Rapid knees.", "vid": "https://www.youtube.com/watch?v=nmwgirgXLYM", "eval": ["Fast Pace", "Knees High"]},
            {"ex": "GLUTE BRIDGES", "sets": 3, "base": 15, "inc": 2, "unit": "reps", "rest": 45, "type": "power", "desc": "Drive hips up.", "vid": "https://www.youtube.com/watch?v=wPM8icPu6H8", "eval": ["Squeeze Glutes", "Heels Down"]},
            {"ex": "BURPEES", "sets": 3, "base": 10, "inc": 2, "unit": "reps", "rest": 90, "type": "cond", "desc": "Full body explosive.", "vid": "https://www.youtube.com/watch?v=dZfeV_pL3fE", "eval": ["Efficiency", "Full Jump"]}
        ]
    }
    return workouts.get(sport, [])

# --- 3. Sidebar Profile ---
st.sidebar.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="margin:0; font-weight:800; font-size:14px;">STREAK</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p style="font-size:36px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 4. Main App UI ---
st.markdown(f"<h1>{sport_choice} Session</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

for i, item in enumerate(drills):
    drill_key = f"{sport_choice}_{i}"
    if drill_key not in st.session_state: st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<p class="stat-label">Target Sets</p><p class="stat-value">{item["sets"]}</p>', unsafe_allow_html=True)
    with c2:
        reps_val = int((item['base'] + ((week_num - 1) * item['inc'])) * target_mult)
        st.markdown(f'<p class="stat-label">Reps/Time</p><p class="stat-value">{reps_val} {item["unit"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="stat-label">Completed</p><p class="stat-value">{st.session_state[drill_key]}</p>', unsafe_allow_html=True)

    # DONE AND REST BUTTONS ON SAME LINE
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
    for idx, criteria in enumerate(item['eval']):
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
    st.session_state.session_saved = True

if st.session_state.session_saved:
    st.info("Session saved. Drink water and stretch!")
