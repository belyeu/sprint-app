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
    sidebar_text = "#FFFFFF" # White text for Dark Mode
    sidebar_label = "#00E5FF"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue = "#006064" # Deep Teal for visibility in Light Mode
    sidebar_text = "#111111" # Near-Black text for Sidebar visibility
    sidebar_label = "#1E40AF" # Strong Navy for labels

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    /* Main Content Text */
    h1, h2, h3, p, span, li {{ color: {text} !important; }}

    /* Sidebar Visibility Overrides */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
        font-weight: 800 !important;
    }}

    /* Specific Sidebar Checkbox Labels */
    [data-testid="stSidebar"] .stCheckbox label p {{
        color: {sidebar_text} !important;
    }}

    /* Electric Blue Labels (Target Set, Reps, etc) */
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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

# --- 3. WORKOUT DATABASE ---
def get_workout_template(sport, locs):
    workouts = {
        "Basketball": [
            {
                "ex": "POUND SERIES", 
                "desc": "High-intensity dribbling focusing on wrist strength. 50 reps at ankle, waist, and shoulder height.", 
                "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", 
                "demo": "https://www.youtube.com/watch?v=7pD_2v8Y-kM",
                "focus": ["Eyes Up", "Wrist Snap", "Ball Pocketing"]
            },
            {
                "ex": "MIKAN SERIES", 
                "desc": "Alternating layups using the backboard. Soft touch and high hands.", 
                "sets": 4, "base": 20, "unit": "reps", "rest": 45, "loc": "Gym", 
                "demo": "https://www.youtube.com/watch?v=3S_v_X_UOnE",
                "focus": ["Soft Touch", "High Hands", "Rhythm"]
            }
        ],
        "Softball": [
            {
                "ex": "TEE WORK", 
                "desc": "Mechanical refinement. Focus on the load phase and level swing path.", 
                "sets": 4, "base": 25, "unit": "swings", "rest": 60, "loc": "Batting Cages", 
                "demo": "https://www.youtube.com/watch?v=W0-qj1i5q_0",
                "focus": ["Hand Path", "Hip Rotation", "Point of Contact"]
            },
            {
                "ex": "TRANSFERS", 
                "desc": "Infield quickness. Fastest possible transfer from glove to hand.", 
                "sets": 3, "base": 30, "unit": "reps", "rest": 30, "loc": "Softball Field", 
                "demo": "https://www.youtube.com/watch?v=eB80tF_XG0k",
                "focus": ["Quick Release", "Four-Seam Grip", "Foot Alignment"]
            }
        ]
    }
    all_drills = workouts.get(sport, [])
    return [d for d in all_drills if d['loc'] in locs]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">TODAY'S DATE</p>
        <p style="margin:0; font-size:18px; font-weight:900; color:{sidebar_text};">{get_now_est().strftime('%B %d, %Y')}</p>
        <p style="margin:0; font-size:14px; opacity:0.8; color:{sidebar_text};">{get_now_est().strftime('%I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

    sport_choice = st.selectbox("Sport Select", ["Basketball", "Softball", "Track", "General Workout"])
    
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
        <p style="margin:0; font-size:22px; font-weight:900; color:{sidebar_text};">{st.session_state.streak} DAYS</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title("PRO-ATHLETE TRACKER")

drills = get_workout_template(sport_choice, active_locs)
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if not drills:
    st.info("Select your training locations in the sidebar to generate drills.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{item["ex"]} <small style="opacity:0.6;">({item["loc"]})</small></div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Target Set", value=str(item["sets"]), key=f"ts_{i}")
        with c2: 
            val = int(item["base"] * target_mult)
            st.text_input("Reps/Time", value=f"{val} {item['unit']}", key=f"rt_{i}")
        with c3: st.checkbox("Mark Done", key=f"f_{i}")
        
        st.markdown(f"<p style='color:{electric_blue}; font-weight:900; margin-bottom:5px; margin-top:10px;'>COACH'S EVAL (FOCUS POINTS)</p>", unsafe_allow_html=True)
        f_cols = st.columns(len(item["focus"]))
        for idx, point in enumerate(item["focus"]):
            with f_cols[idx]:
                st.checkbox(point, key=f"focus_{i}_{idx}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"LOG DRILL ✅", key=f"log_{i}", use_container_width=True):
                st.toast(f"{item['ex']} Logged!")
        with col_b:
            rest_val = int(item["rest"] * rest_mult)
            if st.button(f"REST {rest_val}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_val, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:36px; color:{electric_blue}; font-weight:900;'>{t}s Remaining</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        with st.expander("🎥 EXERCISE DEMO & VIDEO UPLOAD"):
            if item["demo"]: st.video(item["demo"])
            st.file_uploader("Upload Training Clip", type=["mp4", "mov"], key=f"v_{i}")

# --- 6. SUMMARY ---
st.divider()
st.markdown("### 📊 SESSION SUMMARY")
if st.button("GENERATE SUMMARY TABLE", use_container_width=True):
    summary = []
    for i, item in enumerate(drills):
        done = "Completed" if st.session_state.get(f"f_{i}") else "Pending"
        summary.append({"Drill": item["ex"], "Status": done, "Location": item["loc"]})
    st.table(pd.DataFrame(summary))

if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Session archived!")
