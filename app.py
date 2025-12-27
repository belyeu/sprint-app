import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & FEATURE INTEGRITY ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'streak' not in st.session_state: st.session_state.streak = 1
if 'history' not in st.session_state: st.session_state.history = []

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEME & VISIBILITY CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue = "#00E5FF"
    sidebar_text = "#FFFFFF"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue = "#006064" 
    sidebar_text = "#111111"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    h1, h2, h3, p, span, li {{ color: {text} !important; }}

    /* Sidebar High-Contrast Overrides */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
        font-weight: 800 !important;
    }}

    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }}

    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; 
        color: {accent} !important;
        background-color: {header_bg}; border-left: 8px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 30px;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FULL WORKOUT DATABASE (54 DRILLS TOTAL) ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at 3 heights.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=7pD_2v8Y-kM", "focus": ["Eyes Up", "Wrist Snap", "Ball Pocketing"]},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups with high hands.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=3S_v_X_UOnE", "focus": ["Soft Touch", "High Hands", "Rhythm"]},
            {"ex": "KNEE-TO-TOE DRIBBLE", "desc": "Rapid height variation handling.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=2qBWbYT24OE", "focus": ["Low Stance", "Hand Speed", "Control"]},
            {"ex": "BOX JUMPS", "desc": "Explosive vertical vertical power.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=asS8m8Sly2c", "focus": ["Soft Landing", "Full Extension", "Arm Swing"]},
            {"ex": "CONTACT LAYUPS", "desc": "Finishing through simulated pressure.", "sets": 4, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=JaHxR1yeo-k", "focus": ["Strong Core", "Focus", "High Finish"]},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral agility and speed.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=L9V6K9OQ-m4", "focus": ["Stay Low", "Active Hands", "No Crossing"]},
            {"ex": "WALL SITS", "desc": "Isometric leg endurance.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=XULOKw4E6P8", "focus": ["90 Deg", "Flat Back", "Heels"]},
            {"ex": "JAB-STEP COUNTER", "desc": "Freezing defenders with triple threat.", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=2qBWbYT24OE", "focus": ["Hard Jab", "Explosive Step", "Eyes Up"]},
            {"ex": "MED BALL TWISTS", "desc": "Rotational power for passing.", "sets": 3, "base": 20, "unit": "reps", "rest": 45, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=H77LofS8tqM", "focus": ["Core Snap", "Head Still", "Speed"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Mechanical refinement and path.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": "https://www.youtube.com/watch?v=W0-qj1i5q_0", "focus": ["Path", "Hip Drive", "Contact"]},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid transfer speed drill.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=eB80tF_XG0k", "focus": ["Quick Release", "Grip", "Footing"]},
            {"ex": "INSIDE PITCH PULLS", "desc": "Quick hands on inside pitches.", "sets": 4, "base": 15, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": "https://www.youtube.com/watch?v=leDfLWdAZQk", "focus": ["Hands First", "Hips", "Finish"]},
            {"ex": "PICKER HOPS", "desc": "Fielding velocity decision-making.", "sets": 3, "base": 20, "unit": "reps", "rest": 45, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=BDk1_Oytv5w", "focus": ["Short Steps", "Glove Down", "Balance"]},
            {"ex": "LONG TOSS", "desc": "Arm strength and distance.", "sets
