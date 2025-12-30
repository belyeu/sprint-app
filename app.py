import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. IMAGE ASSETS ---
IMAGE_ASSETS = {
    "Softball": ["IMG_3874.jpeg", "IMG_3875.jpeg"],
    "General": ["IMG_3876.jpeg", "IMG_3877.jpeg"],
    "Track": ["IMG_3881.jpeg"]
}

# --- 3. SIDEBAR: RESTORED OPTIONS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor"],
        default=["Gym", "Field"]
    )
    num_drills = st.slider("Exercises", 5, 20, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

# --- 4. CSS: VISIBILITY FIXES ---
if dark_mode:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#0F172A", "#1E293B", "#F8FAFC", "#94A3B8", "#3B82F6", "#FFFFFF"
else:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#FFFFFF", "#F1F5F9", "#0F172A", "#475569", "#2563EB", "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Exercise Name Visibility */
    [data-testid="stExpander"] summary p {{
        color: {text_color} !important;
        font-weight: 700 !important;
    }}

    /* Button Visibility (Force solid colors, no hover required) */
    div.stButton > button {{
        background-color: {accent} !important;
        color: {btn_text} !important;
        border: none !important;
        opacity: 1 !important;
    }}

    .metric-label {{ font-size: 0.75rem; color: {sub_text}; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1rem; color: {accent}; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOADING (ALL 13 FIELDS) ---
def load_data(sport):
    urls = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/track.csv",
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/general.csv"
    }
    try:
        df = pd.read_csv(urls[sport]).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        data_list = []
        for _, row in df.iterrows():
            img_options = IMAGE_ASSETS.get(sport, [])
            assigned_img = random.choice(img_options) if img_options else None
            data_list.append({
                "ex": row.get('Exercise Name', 'Exercise'),
                "env": row.get('Env.', 'Gym'),
                "category": row.get('Category', 'Skill'),
                "cns": row.get('CNS', 'Med'),
                "sets": int(row.get('Sets')) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist', 'N/A'),
                "time": str(row.get('Time', '60s')),
                "focus": row.get('Primary Focus', 'Technique'),
                "stars": row.get('Stars', '⭐⭐⭐'),
                "pre_req": row.get('Pre-Req', 'None'),
                "hs_goals": row.get('HS Goals', 'N/A'),
                "college_goals": row.get('College Goals', 'N/A'),
                "desc": row.get('Description', 'No details.'),
                "demo": str(row.get('Demo', '')).strip(),
                "static_img": assigned_img
            })
        return data_list
    except: return []

# --- 6. GENERATION ---
if st.sidebar.button("🚀 GENERATE WORKOUT"):
    pool = load_data(sport_choice)
    filtered = [d for d in pool if d['env'] in location_filter] or pool
    st.session_state.current_session = random.sample(filtered, min(len(filtered), num_drills))
    st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
    st.session_state.workout_finished = False

# --- 7. MAIN UI ---
st.markdown(f"<h1 style='text-align: center; color: {accent};'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']} {drill['stars']}", expanded=(i==0)):
            col_img, col_meta = st.columns([1, 2])
            with col_img:
                if drill['static_img']: st.image(drill['static_img'], use_container_width=True)
            with col_meta:
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<p class='metric-label'>CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='metric-label'>SETS</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<p class='metric-label'>REST</p><p class='metric-value'>{drill['time']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='metric-label'>ENV</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)

            st.divider()
            st.write(f"**Description:** {drill['desc']}")
            st.info(f"**HS Goal:** {drill['hs_goals']} | **College Goal:** {drill['college_goals']}")
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"Log Set ({curr}/{drill['sets']})", key=f"l_{i}"):
                    st.session_state.set_counts[i] = min(curr + 1, drill['sets'])
                    st.rerun()
                if drill['demo'].startswith('http'): st.video(drill['demo'])
            
            with c2:
                try: r_time = int(''.join(filter(str.isdigit, drill['time'])))
                except: r_time = 60
                if st.button(f"Start {r_time}s Rest", key=f"t_{i}"):
                    ph = st.empty()
                    for t in range(r_time, -1, -1):
                        ph.metric("Resting", f"{t}s")
                        time.sleep(1)
                    st.toast("Rest Over!")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()
elif st.session_state.workout_finished:
    st.success("Session Complete!")
    if st.button("Restart"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
