import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"name": "Elite Athlete", "sport": "General", "level": "Pro"}

# --- 2. SIDEBAR (LOCATION, INTENSITY, TIMER) ---
with st.sidebar:
    st.markdown("# 🛡️ ATHLETE HUB")
    
    # PROFILE SECTION
    with st.expander("👤 User Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["level"] = st.select_slider("Level", ["Rookie", "Varsity", "College", "Pro"])
    
    st.divider()

    # LOCATION / SPORT SELECTOR
    st.header("📍 LOCATION FILTER")
    sport_options = ["General", "Basketball", "Softball", "Track"]
    selected_sport = st.selectbox("Select Training Site", sport_options)
    
    # INTENSITY METER
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Current Effort", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

    st.divider()

    # REST TIMER (Shared Sidebar Timer)
    st.header("⏱️ QUICK REST")
    q_rest = st.number_input("Manual Seconds", 0, 300, 60, step=5)
    if st.button("Start Manual Timer", use_container_width=True):
        ph = st.empty()
        for t in range(q_rest, -1, -1):
            ph.metric("Resting...", f"{t}s")
            time.sleep(1)
        st.balloons()

# --- 3. DATA LOADER (FIXING UNKNOWN NAMES) ---
@st.cache_data
def load_data(sport):
    urls = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    try:
        df = pd.read_csv(urls[sport])
        df.columns = [c.strip() for c in df.columns] # Remove hidden spaces
        
        data_list = []
        for _, row in df.iterrows():
            # EXTENDED KEY MAPPING FOR EXERCISE NAMES
            name = (row.get('exercise') or row.get('Exercise') or 
                    row.get('Exercise Name') or row.get('Drill / Move Name') or 
                    row.get('Drill') or "Unnamed Drill")
            
            desc = row.get('Detailed Description') or row.get('Description') or "No description provided."
            sets = row.get('Sets', 3)
            reps = row.get('Reps/Dist.') or row.get('Base') or "10"
            video = row.get('Video URL') or ""
            
            # EXTRACT SPECIFIC REST TIME (e.g., "60s" -> 60)
            rest_raw = str(row.get('Rest', '60'))
            rest_val = "".join(filter(str.isdigit, rest_raw))
            rest_seconds = int(rest_val) if rest_val else 60
            
            data_list.append({
                "ex": name, "desc": desc, "video": video,
                "sets": int(sets) if str(sets).isdigit() else 3, 
                "reps": reps, "rest": rest_seconds
            })
        return data_list
    except:
        return []

# --- 4. GENERATE SESSION ---
with st.sidebar:
    num_drills = st.slider("Drill Count", 12, 15, 13)
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(selected_sport)
        if pool:
            st.session_state.current_session = random.sample(pool, min(len(pool), num_drills))
            st.session_state.active_sport = selected_sport

# --- 5. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.user_profile['name']}'s {st.session_state.active_sport} Session")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i==0)):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Instructions:** {drill['desc']}")
                
                # REST BUTTON SPECIFIC TO EXERCISE
                if st.button(f"⏱️ Start {drill['rest']}s Rest", key=f"rest_btn_{i}"):
                    ph = st.empty()
                    for t in range(drill['rest'], -1, -1):
                        ph.metric("Recovering...", f"{t}s")
                        time.sleep(1)
                    ph.success("Go!")

                # SET TRACKER AS BUTTONS
                st.markdown("#### 🔢 Progress Tracker")
                btn_cols = st.columns(drill['sets'])
                for s in range(drill['sets']):
                    if btn_cols[s].button(f"Set {s+1}", key=f"btn_{i}_{s}"):
                        st.toast(f"Set {s+1} of {drill['ex']} complete!")

            with c2:
                st.markdown("#### 📺 Demo & Form")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                
                st.file_uploader("Upload Your Form", type=['mp4', 'mov'], key=f"up_{i}")
                
                if st.button(f"Log PR", key=f"pr_{i}"):
                    st.success("Record Saved!")
else:
    st.info("👋 Select a Location and click 'Generate Workout' in the sidebar.")
