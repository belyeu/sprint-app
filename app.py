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
    with st.expander("👤 User Profile Settings"):
        st.session_state.user_profile["name"] = st.text_input("Athlete Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["level"] = st.select_slider("Skill Level", ["Rookie", "Varsity", "College", "Pro"])
    
    st.markdown(f"**Athlete:** {st.session_state.user_profile['name']} | **Level:** {st.session_state.user_profile['level']}")
    st.divider()

    # LOCATION / SPORT SELECTOR (The "Missing" Selector)
    st.header("📍 SESSION SETUP")
    sport_options = ["General", "Basketball", "Softball", "Track"]
    selected_sport = st.selectbox("Select Training Location/Sport", sport_options)
    num_drills = st.slider("Exercises per Session", 12, 15, 13)
    
    # INTENSITY METER
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Current Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])
    st.write(f"Training at **{effort}** intensity.")

    st.divider()

    # REST TIMER
    st.header("⏱️ REST TIMER")
    timer_val = st.number_input("Seconds", 0, 300, 60, step=5)
    if st.button("Start Timer", use_container_width=True):
        ph = st.empty()
        for t in range(timer_val, -1, -1):
            ph.metric("Rest Remaining", f"{t}s")
            time.sleep(1)
        st.balloons()
        ph.success("Work!")

# --- 3. THEME & DATA LOADING ---
st.markdown(f"""<style>
    .stApp {{ background-color: #0F172A; color: #F8FAFC; }}
    [data-testid="stExpander"] {{ background-color: #1E293B !important; border: 1px solid #3B82F6 !important; border-radius: 12px; }}
</style>""", unsafe_allow_html=True)

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
        # Clean column names to prevent "Unknown"
        df.columns = [c.strip() for c in df.columns]
        data_list = []
        for _, row in df.iterrows():
            # Robust mapping for different CSV headers
            name = row.get('Exercise') or row.get('Drill / Move Name') or row.get('Drill') or "Unnamed Drill"
            desc = row.get('Detailed Description') or row.get('Description') or "Perform with max effort."
            sets = row.get('Sets', 3)
            reps = row.get('Reps/Dist.') or row.get('Base') or "To Failure"
            video = row.get('Video URL') or ""
            
            data_list.append({"ex": name, "desc": desc, "sets": int(sets) if str(sets).isdigit() else 3, "reps": reps, "video": video})
        return data_list
    except:
        return []

# --- 4. GENERATE SESSION ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(selected_sport)
        if pool:
            st.session_state.current_session = random.sample(pool, min(len(pool), num_drills))
            st.session_state.active_sport = selected_sport
        else:
            st.error("Could not load data. Check CSV headers.")

# --- 5. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.active_sport} Session | Intensity: {effort}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i==0)):
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Instructions:** {drill['desc']}")
                st.markdown("#### 🔢 Progress Tracker")
                for s in range(drill['sets']):
                    st.checkbox(f"Set {s+1} ({drill['reps']})", key=f"check_{selected_sport}_{i}_{s}")
                
                st.markdown("#### 📤 Form Upload")
                st.file_uploader("Upload Clip", type=['mp4', 'mov'], key=f"up_{i}")

            with c2:
                st.markdown("#### 📺 Demo Video")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                else:
                    st.warning("No demo video available for this exercise.")
                
                if st.button(f"Log PR for {drill['ex']}", key=f"pr_{i}"):
                    st.toast(f"New PR logged for {drill['ex']}!")
else:
    st.info("👋 Use the sidebar to select your sport and 'Generate Workout' to begin.")
