import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"name": "Elite Athlete", "sport": "General", "level": "Pro"}
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}

# --- 2. SIDEBAR: PROFILE, LOCATION, INTENSITY ---
with st.sidebar:
    st.markdown("# 🛡️ ATHLETE HUB")
    
    # PROFILE
    with st.expander("👤 Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
    
    st.divider()

    # LOCATION FILTERS (NEW)
    st.header("📍 LOCATION & SPORT")
    sport_choice = st.selectbox("Sport", ["General", "Basketball", "Softball", "Track"])
    location_filter = st.multiselect(
        "Filter by Facility", 
        ["Gym", "Field", "Cages", "Weight Room", "Track"],
        default=["Gym", "Field"]
    )
    num_drills = st.slider("Exercises", 12, 15, 13)
    
    st.divider()

    # INTENSITY METER (FIXED LOCATION)
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

    st.divider()

    # DYNAMIC REST TIMER
    st.header("⏱️ REST TIMER")
    # This will update based on the active exercise's specific rest time
    default_rest = 60
    if st.session_state.current_session:
        # Pulls rest from the first exercise as a default if not specified
        try:
            raw_rest = st.session_state.current_session[0]['rest']
            default_rest = int(''.join(filter(str.isdigit, str(raw_rest))))
        except:
            default_rest = 60

    timer_val = st.number_input("Seconds", 0, 300, default_rest, step=5)
    if st.button("Start Timer", use_container_width=True):
        ph = st.empty()
        for t in range(timer_val, -1, -1):
            ph.metric("Resting...", f"{t}s")
            time.sleep(1)
        st.balloons()
        ph.success("Go!")

# --- 3. DATA LOADING (FIXING "UNKNOWN" & HEADERS) ---
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
        df.columns = [c.strip() for c in df.columns] # Clean whitespace
        
        data_list = []
        for _, row in df.iterrows():
            # SPECIFIC HEADER MATCHING FOR "EXERCISE" OR "EXERCISE NAME"
            name = row.get('Exercise') or row.get('Exercise Name') or row.get('Drill / Move Name') or "Unnamed Drill"
            desc = row.get('Detailed Description') or row.get('Description') or "No description provided."
            sets = row.get('Sets', 3)
            reps = row.get('Reps/Dist.') or row.get('Base') or "10"
            video = row.get('Video URL') or ""
            rest_period = row.get('Rest') or "60s"
            
            data_list.append({
                "ex": name, 
                "desc": desc, 
                "sets": int(sets) if str(sets).isdigit() else 3, 
                "reps": reps, 
                "video": video,
                "rest": rest_period
            })
        return data_list
    except:
        return []

# --- 4. GENERATE SESSION ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(sport_choice)
        if pool:
            # We select drills, normally you'd filter by 'location' column if it exists in CSV
            st.session_state.current_session = random.sample(pool, min(len(pool), num_drills))
            st.session_state.active_sport = sport_choice
            st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}

# --- 5. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.active_sport} @ {', '.join(location_filter)}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i==0)):
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Instructions:** {drill['desc']}")
                st.write(f"**Target:** {drill['sets']} Sets x {drill['reps']}")
                st.write(f"**Specific Rest:** {drill['rest']}")
                
                # ONE BUTTON COUNTER (NEW)
                st.markdown("#### 🔢 Set Counter")
                current_sets = st.session_state.set_counts.get(i, 0)
                
                col_btn, col_txt = st.columns([1, 2])
                if col_btn.button(f"Log Set", key=f"btn_{i}"):
                    if st.session_state.set_counts[i] < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                col_txt.markdown(f"### Progress: {st.session_state.set_counts[i]} / {drill['sets']}")
                
                if st.session_state.set_counts[i] >= drill['sets']:
                    st.success("✅ Exercise Complete!")

            with c2:
                st.markdown("#### 📺 Demo & Form")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                
                st.file_uploader("Upload Form Clip", type=['mp4', 'mov'], key=f"up_{i}")

else:
    st.info("👋 Select your Sport and Locations in the sidebar to begin.")
