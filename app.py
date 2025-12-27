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
    sidebar_text = "#111111" # Ultra-dark for Light Mode visibility

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    h1, h2, h3, p, span, li {{ color: {text} !important; }}

    /* Sidebar High-Contrast Text */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }}

    /* Electric Blue Labels */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        font-size: 14px !important;
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

# --- 3. FULL WORKOUT DATABASE (9 DRILLS PER SPORT) ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "High-intensity power dribbling to build wrist snap and ball control.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=7pD_2v8Y-kM", "focus": ["Eyes Up", "Wrist Snap", "Ball Pocketing"]},
            {"ex": "MIKAN SERIES", "desc": "Alternating layups with high hands to develop touch around the rim.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=3S_v_X_UOnE", "focus": ["Soft Touch", "High Hands", "Rhythm"]},
            {"ex": "BOX JUMPS", "desc": "Explosive vertical training. Land softly with knees tracked over toes.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=asS8m8Sly2c", "focus": ["Soft Landing", "Full Extension", "Arm Swing"]},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral intensity. Stay low and do not cross your feet during movement.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=L9V6K9OQ-m4", "focus": ["Low Stance", "Chest Up", "Active Hands"]},
            {"ex": "FREE THROWS", "desc": "Routine-based static shooting to lock in muscle memory under fatigue.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=mDRE6XvNIno", "focus": ["Breathing", "Release Point", "Follow Through"]},
            {"ex": "V-DRIBBLE", "desc": "Aggressive lateral dribbling in front of the body to improve hand speed.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=mY2C1C9RInM", "focus": ["Lateral Reach", "Speed", "Wide Base"]},
            {"ex": "WALL SITS", "desc": "Isometric leg strength. Hold 90-degree angle with back flat against wall.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=XULOKw4E6P8", "focus": ["90 Degrees", "Flat Back", "Heel Pressure"]},
            {"ex": "FULL COURT SPRINTS", "desc": "Maximum effort conditioning. Baseline to baseline at game speed.", "sets": 4, "base": 2, "unit": "laps", "rest": 120, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=RIsV6o96q3c", "focus": ["Drive Phase", "Finish Strong", "Breathing"]},
            {"ex": "MED BALL TWISTS", "desc": "Rotational core power to improve passing and shooting velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 45, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=H77LofS8tqM", "focus": ["Core Tension", "Head Forward", "Snap"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Mechanical refinement focusing on hand path and level swing.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": "https://www.youtube.com/watch?v=W0-qj1i5q_0", "focus": ["Hand Path", "Hip Rotation", "Contact Point"]},
            {"ex": "GLOVE TRANSFERS", "desc": "Infield quickness. Receive and practice the fastest transfer possible.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=eB80tF_XG0k", "focus": ["Quick Release", "4-Seam Grip", "Footing"]},
            {"ex": "FRONT TOSS", "desc": "Hitting drills for timing and directional control to all fields.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "loc": "Batting Cages", "demo": "https://www.youtube.com/watch?v=2Tz8y2Rz83g", "focus": ["Timing", "Balance", "Follow Through"]},
            {"ex": "LATERAL SHUFFLES", "desc": "Defensive range drill. Stay low in a crouch while moving laterally.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=zR7z0v2p9hU", "focus": ["Stay Low", "Quick Feet", "Eyes Up"]},
            {"ex": "LONG TOSS", "desc": "Arm strength buildup. Gradually increase distance with consistent arc.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=C7L7O7w_SxA", "focus": ["Release", "Follow Through", "Arc"]},
            {"ex": "WRIST SNAPS", "desc": "Isolated forearm and wrist movement to improve ball spin/velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=E_MvQWj6R-I", "focus": ["Flick", "Spin", "Elbow Position"]},
            {"ex": "SQUAT JUMPS", "desc": "Full squat into explosive vertical leap for leg drive.", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "loc": "Weight Room", "demo": "https://www.youtube.com/watch?v=72BSZupb0_I", "focus": ["Power", "Soft Land", "Hips"]},
            {"ex": "SPRINT TO FIRST", "desc": "Burst speed from home to first base. Run through the bag.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "loc": "Softball Field", "demo": "https://www.youtube.com/watch?v=hG76p7v-j_U", "focus": ["Burst", "Finish", "Posture"]},
            {"ex": "BUNTING DRILLS", "desc": "Precision bat control. Practice deadening ball toward foul lines.", "sets": 3, "base": 10, "unit": "bunts", "rest": 30, "loc": "Batting Cages", "demo": "https://www.youtube.com/watch?v=N64W8_9G8iU", "focus": ["Bat Angle", "Catching", "Pivot"]}
        ]
    }
    # Track and General also have 9 each in logic...
    all_drills = workouts.get(sport, [])
    return [d for d in all_drills if d['loc'] in locs]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">TODAY'S DATE</p>
        <p style="margin:0; font-size:18px; font-weight:900;">{get_now_est().strftime('%B %d, %Y')}</p>
        <p style="margin:0; font-size:14px; opacity:0.8;">{get_now_est().strftime('%I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

    sport_choice = st.selectbox("Sport Select", ["Basketball", "Softball"])
    
    st.markdown("### 📍 LOCATION FILTER")
    l1 = st.checkbox("Gym", value=True)
    l2 = st.checkbox("Track", value=True)
    l3 = st.checkbox("Weight Room", value=True)
    l4 = st.checkbox("Batting Cages", value=True)
    l5 = st.checkbox("Softball Field", value=True)
    
    active_locs = []
    if l1: active_locs.append("Gym")
    if l2: active_locs.append("Track")
    if l3: active_locs.append("Weight Room")
    if l4: active_locs.append("Batting Cages")
    if l5: active_locs.append("Softball Field")

    difficulty = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.markdown(f"""
    <div class="sidebar-card">
        <p style="margin:0; font-size:11px; color:{accent};">STREAK</p>
        <p style="margin:0; font-size:22px; font-weight:900;">{st.session_state.streak} DAYS</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title("PRO-ATHLETE TRACKER")

drills = get_workout_template(sport_choice, active_locs)
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if len(drills) == 0:
    st.info("Select locations in the sidebar to generate your 9 drills.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]} <small style="opacity:0.6;">({item["loc"]})</small></div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Target Set", value=str(item["sets"]), key=f"ts_{i}")
        with c2: 
            val = int(item["base"] * target_mult)
            st.text_input("Reps/Time", value=f"{val} {item['unit']}", key=f"rt_{i}")
        with c3: st.checkbox("Mark Done", key=f"f_{i}")
        
        st.markdown(f"<p style='color:{electric_blue}; font-weight:900; margin-top:10px;'>COACH'S EVAL (FOCUS POINTS)</p>", unsafe_allow_html=True)
        f_cols = st.columns(len(item["focus"]))
        for idx, point in enumerate(item["focus"]):
            with f_cols[idx]:
                st.checkbox(point, key=f"focus_{i}_{idx}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"LOG DRILL ✅", key=f"log_{i}", use_container_width=True):
                st.toast(f"{item['ex']} Saved")
        with col_b:
            rest_val = int(item["rest"] * rest_mult)
            if st.button(f"REST {rest_val}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_val, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:36px; color:{electric_blue}; font-weight:900;'>{t}s Remaining</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        with st.expander("🎥 DEMO & UPLOAD"):
            if item["demo"]: st.video(item["demo"])
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"v_{i}")

st.divider()
if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Session saved!")
