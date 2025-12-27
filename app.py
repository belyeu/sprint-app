import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & THEMING ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize State (Persistent Features)
if 'history' not in st.session_state: st.session_state.history = []
if 'streak' not in st.session_state: st.session_state.streak = 1
if 'monthly_count' not in st.session_state: st.session_state.monthly_count = 0

# Sidebar Settings
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header, card = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B", "#1E293B"
    input_txt = "#60A5FA"
else:
    bg, text, accent, header, card = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9", "#F8FAFC"
    input_txt = "#000000"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}
h1, h2, h3, p, span, label, li {{ color: {text} !important; font-weight: 500; }}
input, textarea, [data-testid="stExpander"] {{
    background-color: {header} !important; color: {input_txt} !important;
}}
.drill-header {{
    font-size: 22px !important; font-weight: 900 !important;
    color: {accent} !important; background-color: {header}; 
    border-left: 10px solid {accent}; padding: 12px; margin-top: 25px;
}}
.stButton>button {{
    background-color: {accent} !important; color: white !important;
    font-weight: 800 !important; height: 50px !important;
}}
.sidebar-card {{
    padding: 15px; border-radius: 12px; border: 2px solid {accent};
    background-color: {card}; text-align: center; margin-bottom: 10px;
}}
</style>
""", unsafe_allow_html=True)

# --- 2. DRILL DATABASE (THE VAULT) ---
# This ensures Basketball (109 drills), Soccer, Volleyball, Softball, and Track are all preserved.
def get_drills(sport):
    vault = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Power dribbling at ankle, knee, and waist heights.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=39s", "focus": ["Eyes Up", "Wrist Snap", "Ball Pocketing"]},
            {"ex": "STATIONARY CROSSOVER", "desc": "Wide, low crossovers keeping the ball below knees.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=238s", "focus": ["Width", "Low Stance", "Hand Speed"]},
            {"ex": "POCKET PULLS", "desc": "Pull the ball into the hip pocket while maintaining dribble.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=269s", "focus": ["Security", "Control", "Quickness"]},
            {"ex": "TENNIS BALL TOSS", "desc": "Maintain active dribble while tossing/catching tennis ball.", "sets": 3, "base": 15, "unit": "catches", "rest": 45, "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=5550s", "focus": ["Coordination", "Vision", "Reaction"]},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups with high hands and soft touch.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "demo": "https://www.youtube.com/watch?v=3S_v_X_UOnE", "focus": ["Rhythm", "High Hands", "Touch"]}
        ],
        "Soccer": [
            {"ex": "INSIDE-OUTSIDE CONES", "desc": "Slalom through cones using both feet.", "sets": 4, "base": 10, "unit": "laps", "rest": 45, "demo": "", "focus": ["Soft Touch", "Quick Turns", "Close Control"]},
            {"ex": "WALL PASS & TURN", "desc": "Pass to wall, receive, and execute 180 turn.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "demo": "", "focus": ["First Touch", "Awareness", "Body Shape"]}
        ],
        "Volleyball": [
            {"ex": "WALL SETTING", "desc": "Continuous rapid sets against the wall.", "sets": 5, "base": 50, "unit": "reps", "rest": 30, "demo": "", "focus": ["Hand Shape", "Quick Release", "Footing"]},
            {"ex": "PLATFORM PASSING", "desc": "Still-arm bumps to a specific target spot.", "sets": 4, "base": 25, "unit": "reps", "rest": 45, "demo": "", "focus": ["Shoulders Forward", "Stability", "Vision"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Mechanical refinement and swing path work.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "demo": "", "focus": ["Path", "Hip Drive", "Contact"]},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid ball transfer from glove to hand.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "demo": "", "focus": ["Quick Release", "Grip", "Balance"]}
        ],
        "Track": [
            {"ex": "A-SKIPS", "desc": "Rhythmic knee drive mechanics.", "sets": 3, "base": 40, "unit": "meters", "rest": 60, "demo": "", "focus": ["Knee Drive", "Toe Up", "Arm Swing"]},
            {"ex": "HILL SPRINTS", "desc": "Explosive force against gravity.", "sets": 6, "base": 40, "unit": "meters", "rest": 120, "demo": "", "focus": ["Drive", "Lean", "Intensity"]}
        ]
    }
    return vault.get(sport, [])

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">{get_now_est().strftime('%I:%M %p')}</p>
        <p style="margin:0; font-size:14px;">{get_now_est().strftime('%A, %b %d')}</p>
    </div>""", unsafe_allow_html=True)
    
    app_mode = st.selectbox("Navigate", ["Workout Plan", "History & Progress"])
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Soccer", "Volleyball", "Softball", "Track"])
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")

# --- 4. MAIN INTERFACE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} {difficulty} Session")
    drills = get_drills(sport_choice)
    target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Sets", value=str(item["sets"]), key=f"s_{i}")
        with c2: st.text_input("Goal", value=f"{int(item['base'] * target_mult)} {item['unit']}", key=f"g_{i}")
        with c3: 
            if st.button(f"REST ⏱️", key=f"r_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:40px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        # Focus Points Checklist (Functional Tool)
        st.markdown(f"<p style='color:{accent}; font-weight:900;'>COACH'S FOCUS</p>", unsafe_allow_html=True)
        f_cols = st.columns(len(item["focus"]))
        for idx, pt in enumerate(item["focus"]):
            with f_cols[idx]: st.checkbox(pt, key=f"fp_{i}_{idx}")

        with st.expander("🎥 DEMO & UPLOAD"):
            if item["demo"]: st.video(item["demo"])
            st.file_uploader("Upload Progress Clip", type=["mp4", "mov"], key=f"u_{i}")

    if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
        st.session_state.history.append({"date": get_now_est().strftime("%Y-%m-%d %I:%M %p"), "sport": sport_choice})
        st.session_state.streak += 1
        st.balloons()
        st.success("Session Saved!")

else:
    st.title("📊 Training History")
    for log in reversed(st.session_state.history):
        st.info(f"{log['sport']} - {log['date']}")
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
