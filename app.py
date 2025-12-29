import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete",
        "sport": "General",
        "level": "Pro",
        "bio": "Striving for excellence."
    }

# --- 2. SIDEBAR: PROFILE, INTENSITY, & TIMER ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["sport"] = st.selectbox("Sport", ["Basketball", "Softball", "Track", "General"])
        st.session_state.user_profile["level"] = st.select_slider("Level", ["Rookie", "Varsity", "College", "Pro"])
        st.session_state.user_profile["bio"] = st.text_area("Training Goal", st.session_state.user_profile["bio"])

    # Profile Display Card
    st.markdown(f"""
    <div style="background-color:rgba(59, 130, 246, 0.1); padding:15px; border-radius:10px; border-left: 5px solid #3B82F6; margin-bottom:20px;">
        <h3 style="margin:0; font-size:18px;">{st.session_state.user_profile['name']}</h3>
        <p style="margin:0; font-size:14px; opacity:0.8;">{st.session_state.user_profile['sport']} | {st.session_state.user_profile['level']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("📊 INTENSITY METER")
    intensity = st.select_slider("Current Effort", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    st.progress({"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}[intensity])

    st.divider()
    st.header("⏱️ REST TIMER")
    timer_seconds = st.number_input("Set Seconds", min_value=0, value=60, step=5)
    if st.button("Start Rest Timer", use_container_width=True):
        ph = st.empty()
        for t in range(timer_seconds, -1, -1):
            ph.metric("Resting...", f"{t}s")
            time.sleep(1)
        st.balloons()
        ph.success("Back to it!")

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F1F5F9"
text_color = "#F8FAFC" if dark_mode else "#1E293B"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    [data-testid="stExpander"] {{ background-color: {card_bg} !important; border-radius: 12px !important; border: 1px solid #3B82F6 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data
def load_vault():
    files = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    vault = {}
    for sport, url in files.items():
        try:
            df = pd.read_csv(url)
            vault[sport] = []
            for _, row in df.iterrows():
                vault[sport].append({
                    "ex": str(row.get('Exercise') or row.get('Drill / Move Name') or "Unknown"),
                    "desc": str(row.get('Detailed Description') or row.get('Description') or "No details."),
                    "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                    "reps": str(row.get('Reps/Dist.') or row.get('Base', '10')),
                    "video": str(row.get('Video URL', "")),
                    "rest": str(row.get('Rest', '60s'))
                })
        except: continue
    return vault

# --- 5. SESSION GENERATION ---
vault = load_vault()
with st.sidebar:
    st.divider()
    st.header("🏟️ SESSION CONTROL")
    sport_choice = st.selectbox("Sport Database", list(vault.keys()) if vault else ["General"])
    num_drills = st.slider("Exercises", 12, 15, 13)
    if st.button("🚀 GENERATE SESSION", use_container_width=True):
        if sport_choice in vault:
            st.session_state.current_session = random.sample(vault[sport_choice], min(len(vault[sport_choice]), num_drills))
            st.session_state.active_sport = sport_choice

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.user_profile['name']}'s {st.session_state.active_sport} Session")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i == 0)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**🎯 Focus:** {drill['desc']}")
                st.markdown(f"**⏱️ Suggested Rest:** {drill['rest']}")
                
                st.markdown("### 🔢 Set Tracker")
                for s in range(drill['sets']):
                    st.checkbox(f"Set {s+1} Complete ({drill['reps']})", key=f"check_{i}_{s}")
                
                st.markdown("### 📤 Upload Your Form")
                st.file_uploader("Upload clip for analysis", type=['mp4', 'mov'], key=f"upload_{i}")

            with col2:
                st.markdown("### 📺 Demo Video")
                if "http" in drill['video']:
                    st.video(drill['video'])
                else:
                    st.info("No demo video link found in database for this drill.")
                
                if st.button(f"Log PR for {drill['ex']}", key=f"pr_{i}"):
                    st.success("Personal Record Saved to Profile!")
else:
    st.info(f"Welcome, {st.session_state.user_profile['name']}. Select your sport in the sidebar and click 'Generate Session' to begin.")
