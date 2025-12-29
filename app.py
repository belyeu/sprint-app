import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "sport": "General", 
        "level": "Pro",
        "hs_goal": "State Championship",
        "college_goal": "D1 Scholarship"
    }
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}

# --- 2. SIDEBAR: PROFILE, LOCATION, & INTENSITY ---
with st.sidebar:
    st.markdown("# 🛡️ ATHLETE HUB")
    
    with st.expander("👤 Profile & Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])
    
    st.divider()

    # FILTERS: SPORT AND LOCATION
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["General", "Basketball", "Softball", "Track"])
    location_filter = st.multiselect(
        "Facility Location", 
        ["Gym", "Field", "Cages", "Weight Room", "Track"],
        default=["Gym"]
    )
    num_drills = st.slider("Exercises", 12, 15, 13)
    
    st.divider()

    # INTENSITY METER
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        # Data loading triggered here
        pool = [] # Placeholder for load_data function logic
        # Logic to load and filter would go here
        st.session_state.set_counts = {} # Reset counters

# --- 3. DATA LOADING LOGIC ---
def load_data(sport):
    urls = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    try:
        df = pd.read_csv(urls[sport])
        df.columns = [c.strip() for c in df.columns]
        data_list = []
        for _, row in df.iterrows():
            # Robust mapping for "Exercise" or "Exercise Name"
            name = row.get('Exercise') or row.get('Exercise Name') or row.get('Drill / Move Name') or "Unnamed Drill"
            data_list.append({
                "ex": name,
                "desc": row.get('Detailed Description') or row.get('Description') or "No description.",
                "focus": row.get('Primary Focus') or "Performance",
                "stars": row.get('Fitness Stars') or "⭐⭐⭐",
                "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist.') or "10",
                "rest": row.get('Rest') or "60s",
                "video": row.get('Video URL') or ""
            })
        return data_list
    except:
        return []

# --- 4. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

# Display Goals
g1, g2 = st.columns(2)
g1.info(f"**HS Goal:** {st.session_state.user_profile['hs_goal']}")
g2.success(f"**College Goal:** {st.session_state.user_profile['college_goal']}")

if st.session_state.current_session:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']} ({drill['stars']})", expanded=(i==0)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**🎯 Focus:** {drill['focus']}")
                st.markdown(f"**📝 Description:** {drill['desc']}")
                st.write(f"**Goal:** {drill['sets']} Sets x {drill['reps']}")
                
                # 1-BUTTON COUNTER
                st.markdown("---")
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"Complete Set ({curr}/{drill['sets']})", key=f"btn_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] = curr + 1
                        st.rerun()
                
                if curr >= drill['sets']:
                    st.success("Exercise Finished!")

            with col2:
                # IN-EXERCISE REST TIMER
                st.markdown("#### ⏱️ Rest Timer")
                try:
                    seconds = int(''.join(filter(str.isdigit, drill['rest'])))
                except:
                    seconds = 60
                
                if st.button(f"Start {seconds}s Rest", key=f"tmr_{i}"):
                    ph = st.empty()
                    for t in range(seconds, -1, -1):
                        ph.metric("Resting...", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                
                st.markdown("---")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                st.file_uploader("Upload Form", type=['mp4', 'mov'], key=f"up_{i}")
