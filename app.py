import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'current_session' not in st.session_state: st.session_state.current_session = None

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_github():
    # Base URL for Raw content on your main branch
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/main/"
    
    files = {
        "Basketball": "basketball%20drills%20-%20Sheet1.csv",
        "General": "general%20-%20Sheet1.csv",
        "Softball": "softball%20drills%20-%20Sheet1.csv",
        "Track": "track%20drills%20-%20track.csv"
    }
    
    vault = {}

    for sport, filename in files.items():
        url = base_url + filename
        try:
            # Directly read the raw CSV from GitHub
            df = pd.read_csv(url)
            
            vault[sport] = []
            for _, row in df.iterrows():
                # This mapping looks for ANY of these common headers in your files
                name = row.get('Drill / Move Name') or row.get('Exercise') or row.get('Exercise Name') or row.get('Skill / Action')
                
                if pd.notnull(name):
                    vault[sport].append({
                        "ex": str(name),
                        "sets": str(row.get('Sets', '3')),
                        "base": str(row.get('Base')) or str(row.get('Reps/Dist.', '10')),
                        "unit": str(row.get('Unit', 'reps')),
                        "rest": str(row.get('Rest', '60s')),
                        "time_goal": str(row.get('Goal', 'N/A')),
                        "desc": str(row.get('Description')) or str(row.get('Specific Execution / Detail')) or "No description.",
                        "focus": str(row.get('Focus', 'General')).split(',')
                    })
        except Exception as e:
            st.sidebar.warning(f"⚠️ Could not load {sport}. (Check if file is Public)")
            
    return vault

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:#F8FAFC; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#000000; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#1E293B; margin:0; font-weight:bold;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    vault = load_vault_from_github()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Sport Database", sport_options)
    intensity = st.select_slider("Intensity", ["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            # Select 5 random drills
            st.session_state.current_session = random.sample(vault[sport_choice], min(len(vault[sport_choice]), 5))
        else:
            st.error("Select a valid database.")

# --- 4. MAIN DISPLAY ---
if st.session_state.current_session:
    st.title(f"🚀 {sport_choice} Session ({intensity})")
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"Drill {i+1}: {drill['ex']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Work", f"{drill['sets']} x {drill['base']} {drill['unit']}")
            c2.metric("Rest", drill['rest'])
            c3.metric("Goal", drill['time_goal'])
            st.write(f"**Focus:** {', '.join(drill['focus'])}")
            st.info(drill['desc'])
else:
    st.info("Please select a sport and click 'Generate' to load your drills.")
