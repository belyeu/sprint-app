import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"name": "Elite Athlete", "level": "Pro"}
if 'completed_sets' not in st.session_state:
    st.session_state.completed_sets = {}

# --- 2. SIDEBAR (PROFILE, LOCATION, INTENSITY) ---
with st.sidebar:
    st.markdown("# 🛡️ ATHLETE HUB")
    
    with st.expander("👤 Profile Settings"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["level"] = st.select_slider("Level", ["Rookie", "Varsity", "College", "Pro"])

    st.divider()

    # LOCATION & SPORT SELECTORS
    st.header("📍 SESSION SETUP")
    location = st.selectbox("Training Location", ["Gym", "Field", "Cages", "Weight Room", "Track"])
    sport_choice = st.selectbox("Sport Category", ["General", "Basketball", "Softball", "Track"])
    num_drills = st.slider("Drills", 12, 15, 13)
    
    # INTENSITY METER
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    st.progress({"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}[effort])

    st.divider()

    # REST TIMER (Exercise Specific)
    st.header("⏱️ REST TIMER")
    # This will update based on the active exercise below
    default_rest = 60
    timer_val = st.number_input("Seconds", 0, 300, default_rest)
    if st.button("Start Timer", use_container_width=True):
        ph = st.empty()
        for t in range(timer_val, -1, -1):
            ph.metric("Rest Remaining", f"{t}s")
            time.sleep(1)
        st.balloons()
        ph.success("GO!")

# --- 3. DATA LOADING ---
@st.cache_data
def load_vault(sport):
    urls = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    try:
        df = pd.read_csv(urls[sport])
        df.columns = [c.strip() for c in df.columns] # Clean hidden spaces
        drills = []
        for _, row in df.iterrows():
            # KEY FIX: Mapping multiple possible column names for "Exercise"
            name = row.get('exercise') or row.get('Exercise Name') or row.get('Exercise') or row.get('Drill / Move Name') or "Unnamed Drill"
            desc = row.get('Detailed Description') or row.get('Description') or "No description provided."
            rest = str(row.get('Rest', '60')).replace('s', '')
            
            drills.append({
                "ex": name,
                "desc": desc,
                "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist.', '10'),
                "video": row.get('Video URL', ""),
                "rest": int(rest) if rest.isdigit() else 60
            })
        return drills
    except:
        return []

# --- 4. GENERATE SESSION ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_vault(sport_choice)
        if pool:
            st.session_state.current_session = random.sample(pool, min(len(pool), num_drills))
            st.session_state.active_sport = sport_choice
            st.session_state.completed_sets = {} # Reset progress

# --- 5. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center;'>🏆 {location.upper()} TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.user_profile['name']} | {st.session_state.active_sport} @ {location}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"DRILL {i+1}: {drill['ex']}", expanded=(i==0)):
            c1, c2 = st.columns(2)
            
            with c1:
                st.info(f"**Instructions:** {drill['desc']}")
                st.write(f"**Target:** {drill['sets']} Sets x {drill['reps']}")
                st.write(f"**Required Rest:** {drill['rest']}s")
                
                # PROGRESS BUTTON TRACKER
                st.markdown("#### 🔢 Progress")
                current_count = st.session_state.completed_sets.get(i, 0)
                if st.button(f"Mark Set {current_count + 1} Done", key=f"btn_{i}"):
                    if current_count < drill['sets']:
                        st.session_state.completed_sets[i] = current_count + 1
                        st.rerun()
                
                st.progress(min(current_count / drill['sets'], 1.0))
                st.write(f"Completed {current_count} of {drill['sets']} sets.")

                st.markdown("#### 📤 Upload Form")
                st.file_uploader("Form Video", type=['mp4'], key=f"file_{i}")

            with c2:
                st.markdown("#### 📺 Demo")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                else:
                    st.warning("Video tutorial not available for this drill.")
                
                if st.button(f"Log Heavy Set for {drill['ex']}", key=f"pr_{i}"):
                    st.success("Set logged to performance history!")
else:
    st.info("👋 Select your location and sport in the sidebar to begin.")
