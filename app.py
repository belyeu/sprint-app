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
        "hs_goal": "State Championship",
        "college_goal": "D1 Recruitment"
    }
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

# --- 3. SIDEBAR ---
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
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor"],
        default=["Gym", "Field", "Track"]
    )
    num_drills = st.slider("Number of Exercises", 5, 20, 13)

    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

# --- 4. DYNAMIC THEMING & VISIBILITY FIXES ---
if dark_mode:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#0F172A", "#1E293B", "#F8FAFC", "#94A3B8", "#3B82F6", "#FFFFFF"
else:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#FFFFFF", "#F1F5F9", "#0F172A", "#475569", "#2563EB", "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Force Expander Header Visibility */
    [data-testid="stExpander"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {accent}44 !important; 
        border-radius: 12px !important; 
    }}
    [data-testid="stExpander"] summary p {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
    }}

    /* Force Button Visibility (Fix for hover issue) */
    div.stButton > button {{
        background-color: {accent} !important;
        color: {btn_text} !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
        opacity: 1 !important;
    }}

    .metric-label {{ font-size: 0.75rem; color: {sub_text}; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1rem; color: {accent}; font-weight: 600; margin-bottom: 12px; }}
    .stMarkdown p, .stMarkdown li {{ color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOADING ---
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
                "ex": row.get('Exercise Name') or row.get('Exercise') or "Unknown Exercise",
                "env": row.get('Env.') or row.get('Location') or "General",
                "category": row.get('Category') or "Athleticism",
                "cns": row.get('CNS') or "Medium",
                "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist') or row.get('Reps/Dist.') or "N/A",
                "time": str(row.get('Time')) or "60s",
                "focus": row.get('Primary Focus') or "Skill Development",
                "stars": row.get('Stars') or row.get('Fitness Stars') or "⭐⭐⭐",
                "pre_req": row.get('Pre-Req') or "None",
                "hs_goals": row.get('HS Goals') or "N/A",
                "college_goals": row.get('College Goals') or "N/A",
                "desc": row.get('Description') or row.get('Detailed Description') or "No details.",
                "demo": str(row.get('Demo') or row.get('Video URL')).strip(),
                "static_img": assigned_img
            })
        return data_list
    except Exception:
        return []

# --- 6. GENERATION LOGIC ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(sport_choice)
        filtered_pool = [d for d in pool if d['env'] in location_filter] or pool
        st.session_state.current_session = random.sample(filtered_pool, min(len(filtered_pool), num_drills))
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

# --- 7. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center; color: {accent};'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']} | {drill['stars']}", expanded=(i==0)):
            
            col_img, col_meta = st.columns([1, 2])
            with col_img:
                if drill['static_img']:
                    st.image(drill['static_img'], use_container_width=True)
                else:
                    st.markdown(f'<div style="height:150px; background:{card_bg}; border:2px dashed {sub_text}44; border-radius:10px; display:flex; align-items:center; justify-content:center; color:{sub_text};">No Preview</div>', unsafe_allow_html=True)

            with col_meta:
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<div class='metric-label'>ENVIRONMENT</div><div class='metric-value'>{drill['env']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>CNS LOAD</div><div class='metric-value'>{drill['cns']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>CATEGORY</div><div class='metric-value'>{drill['category']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>PRE-REQ</div><div class='metric-value'>{drill['pre_req']}</div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-label'>TARGET SETS</div><div class='metric-value'>{drill['sets']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>REPS/DIST</div><div class='metric-value'>{drill['reps']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>REST TIME</div><div class='metric-value'>{drill['time']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>PRIMARY FOCUS</div><div class='metric-value'>{drill['focus']}</div>", unsafe_allow_html=True)

            st.divider()
            
            g1, g2 = st.columns(2)
            g1.info(f"**HS Goals:** {drill['hs_goals']}")
            g2.success(f"**College Goals:** {drill['college_goals']}")
            st.markdown(f"**Description:** {drill['desc']}")
            
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                curr_sets = st.session_state.set_counts.get(i, 0)
                if st.button(f"Log Set ({curr_sets}/{drill['sets']})", key=f"btn_{i}"):
                    if curr_sets < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                if drill['demo'].startswith('http'):
                    try:
                        st.video(drill['demo'])
                    except:
                        st.caption("Video unavailable.")
                else:
                    st.caption("No video demo.")

            with c2:
                st.markdown("#### ⏱️ Rest Timer")
                try: r_time = int(''.join(filter(str.isdigit, drill['time'])))
                except: r_time = 60
                
                if st.button(f"Start {r_time}s Rest", key=f"t_btn_{i}"):
                    ph = st.empty()
                    for t in range(r_time, -1, -1):
                        ph.metric("Rest Timer", f"{t}s")
                        time.sleep(1)
                    st.toast("Rest Over!")
                    st.balloons()

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.header("📝 Session Complete")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'category', 'sets']])
    if st.button("Restart Dashboard"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👋 Select sport and location in the sidebar to begin.")
