import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
import random
import os

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None
if 'active_sport' not in st.session_state: st.session_state.active_sport = ""

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_csv():
    # Base URL for your specific GitHub repo
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/main/"
    
    # List of your specific files
    files = {
        "Basketball": "basketball%20drills%20-%20Sheet1.csv",
        "General": "general%20-%20Sheet1.csv",
        "Softball": "softball%20drills%20-%20Sheet1.csv",
        "Track": "track%20drills%20-%20track.csv"
    }
    
    vault = {}

    for sport_name, file_name in files.items():
        url = base_url + file_name
        try:
            df = pd.read_csv(url)
            vault[sport_name] = []
            
            for _, row in df.iterrows():
                # Flexible Mapping: Checks different possible column names across your 4 files
                name = row.get('Drill / Move Name') or row.get('Exercise Name') or row.get('Skill / Action') or row.get('Exercise')
                desc = row.get('Specific Execution / Detail') or row.get('Equipment / Focus') or row.get('Thrower/Fielder Mechanics') or row.get('Description')
                
                if pd.notnull(name):
                    vault[sport_name].append({
                        "ex": str(name),
                        "sets": str(row.get('Sets', '3')),
                        "base": str(row.get('Reps/Dist.', '10')) or str(row.get('Base', '10')),
                        "unit": str(row.get('Unit', 'reps')),
                        "rest": str(row.get('Rest', '60s')),
                        "time_goal": str(row.get('Goal', 'N/A')),
                        "desc": str(desc) if pd.notnull(desc) else "No description provided.",
                        "focus": str(row.get('Primary Focus', 'Performance')).split(',')
                    })
        except Exception as e:
            st.sidebar.error(f"⚠️ Error loading {sport_name}: {e}")
            
    return vault

# --- 3. SIDEBAR (BLACK LABELS) ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:#F8FAFC; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#000000; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#1E293B; margin:0; font-weight:bold; letter-spacing:1px;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    location = st.selectbox("Location", ["Gym", "Softball Field", "Track", "Weight Room"])
    
    # Load data from GitHub
    vault = load_vault_from_csv()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Sport Database", sport_options)
    num_drills = st.slider("Drills per Session", 3, 10, 5)
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            # Select random drills based on the slider
            sample_size = min(len(vault[sport_choice]), num_drills)
            st.session_state.current_session = random.sample(vault[sport_choice], sample_size)
            st.session_state.active_sport = sport_choice
        else:
            st.error("No drills found in the selected database.")

# --- 4. MAIN DISPLAY LOGIC ---
if st.session_state.current_session:
    st.title(f"🚀 {st.session_state.active_sport} Session: {difficulty}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"DRILL {i+1}: {drill['ex']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Work", f"{drill['sets']} x {drill['base']} {drill['unit']}")
            col2.metric("Rest", drill['rest'])
            col3.metric("Goal", drill['time_goal'])
            
            st.markdown(f"**Execution:** {drill['desc']}")
            st.caption(f"Focus: {', '.join(drill['focus'])}")
else:
    st.info("Select a Sport Database and click 'Generate New Session' to begin.")
