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
    st.session_state.user_profile = {"name": "Elite Athlete", "hs_goal": "State Championship", "college_goal": "D1 Recruitment"}
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. IMAGE MAPPING ---
IMAGE_ASSETS = {
    "Softball": ["IMG_3874.jpeg", "IMG_3875.jpeg"],
    "General": ["IMG_3876.jpeg", "IMG_3877.jpeg"],
    "Track": ["IMG_3881.jpeg"]
}

# --- 3. SIDEBAR & INTENSITY METER ---
with st.sidebar:
    st.header("🎨 INTERFACE")
    dark_mode = st.toggle("Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Update Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📊 INTENSITY METER")
    # Intensity adjusts the load (sets/reps)
    effort = st.select_slider("Workout Intensity", options=["Recovery", "Standard", "Intense", "Elite"], value="Standard")
    intensity_map = {"Recovery": 0.7, "Standard": 1.0, "Intense": 1.3, "Elite": 1.5}
    intensity_mult = intensity_map[effort]
    st.caption(f"Volume Multiplier: {intensity_mult}x")
    st.progress(int((intensity_mult/1.5)*100))

    st.divider()
    st.header("📂 DATA SOURCE")
    uploaded_file = st.file_uploader("Upload Exercise CSV", type=["csv"])
    
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor"], default=["Gym", "Field"])
    num_drills = st.slider("Exercises", 5, 20, 13)

# --- 4. DYNAMIC THEMING & LIGHT MODE BLUE TEXT ---
if dark_mode:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text, expander_header = "#0F172A", "#1E293B", "#F8FAFC", "#94A3B8", "#3B82F6", "#FFFFFF", "#FFFFFF"
else:
    # Changed expanded text/header to Blue for Light Mode as requested
    primary_bg, card_bg, text_color, sub_text, accent, btn_text, expander_header = "#FFFFFF", "#F1F5F9", "#0F172A", "#475569", "#2563EB", "#FFFFFF", "#2563EB"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    [data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {accent}44 !important; border-radius: 12px !important; }}
    
    /* LIGHT MODE BLUE TEXT FIX */
    [data-testid="stExpander"] summary p {{
        color: {expander_header} !important;
        font-weight: 700 !important;
    }}
    
    div.stButton > button {{
        background-color: {accent} !important;
        color: {btn_text} !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
        opacity: 1 !important;
    }}
    .metric-label {{ font-size: 0.75rem; color: {sub_text}; font-weight: bold; }}
    .metric-value {{ font-size: 1rem; color: {accent}; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOADING ---
def load_data():
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file).fillna("N/A")
    else:
        urls = {
            "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
            "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/softball.csv",
            "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/track.csv",
            "General": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/general.csv"
        }
        df = pd.read_csv(urls[sport_choice]).fillna("N/A")
    
    df.columns = [c.strip() for c in df.columns]
    data_list = []
    for _, row in df.iterrows():
        img_options = IMAGE_ASSETS.get(sport_choice, [])
        # INTENSITY ADJUSTMENT: Adjust sets and time based on slider
        base_sets = int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3
        adj_sets = max(1, int(base_sets * intensity_mult))
        
        data_list.append({
            "ex": row.get('Exercise Name', 'Exercise'),
            "env": row.get('Env.', 'Gym'),
            "category": row.get('Category', 'Skill'),
            "cns": row.get('CNS', 'Med'),
            "sets": adj_sets,
            "reps": row.get('Reps/Dist', 'N/A'),
            "time": str(row.get('Time', '60s')),
            "focus": row.get('Primary Focus', 'Technique'),
            "stars": row.get('Stars', '⭐⭐⭐'),
            "pre_req": row.get('Pre-Req', 'None'),
            "hs_goals": row.get('HS Goals', 'N/A'),
            "college_goals": row.get('College Goals', 'N/A'),
            "desc": row.get('Description', 'No details.'),
            "demo": str(row.get('Demo', '')).strip(),
            "static_img": random.choice(img_options) if img_options else None
        })
    return data_list

# --- 6. GENERATION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    pool = load_data()
    filtered = [d for d in pool if d['env'] in location_filter] or pool
    st.session_state.current_session = random.sample(filtered, min(len(filtered), num_drills))
    st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
    st.session_state.workout_finished = False

# --- 7. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center; color: {accent};'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']} | {drill['stars']}", expanded=(i==0)):
            col_img, col_meta = st.columns([1, 2])
            with col_img:
                if drill['static_img']: st.image(drill['static_img'], use_container_width=True)
            with col_meta:
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<p class='metric-label'>INTENSITY ADJ. SETS</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='metric-label'>CNS LOAD</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<p class='metric-label'>REST TARGET</p><p class='metric-value'>{drill['time']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='metric-label'>ENVIRONMENT</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)

            st.divider()
            st.info(f"**HS Standard:** {drill['hs_goals']} | **College Standard:** {drill['college_goals']}")
            st.write(f"**Instructions:** {drill['desc']}")
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                # LOG SET BUTTON
                if st.button(f"Log Set ({curr}/{drill['sets']})", key=f"log_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        # START REST TIMER IMMEDIATELY AFTER LOGGING
                        st.session_state[f"active_rest_{i}"] = True
                        st.rerun()

                if drill['demo'].startswith('http'): st.video(drill['demo'])

            with c2:
                # AUTO-TRIGGERED REST TIMER
                try: r_time = int(''.join(filter(str.isdigit, drill['time'])))
                except: r_time = 60
                
                if st.session_state.get(f"active_rest_{i}", False):
                    ph = st.empty()
                    for t in range(r_time, -1, -1):
                        ph.metric("Resting... Get ready for next set!", f"{t}s")
                        time.sleep(1)
                    st.session_state[f"active_rest_{i}"] = False
                    st.toast("Rest Over! Go!")
                    st.rerun()
                else:
                    st.write("Click 'Log Set' to trigger rest timer.")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Great training session!")
    if st.button("New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
