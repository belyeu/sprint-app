import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'active_sport' not in st.session_state:
    st.session_state.active_sport = ""

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_csv():
    # Corrected URLs with exact space encoding (%20)
    # Basketball: single space | General: double space | Softball: double space
    files = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general%20%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball%20drills%20%20-%20Sheet1.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    
    vault = {}

    for sport_name, url in files.items():
        try:
            # pd.read_csv handles the URL directly
            df = pd.read_csv(url)
            vault[sport_name] = []
            
            for _, row in df.iterrows():
                # Checking all common header names from your sheets
                name = row.get('Drill / Move Name') or row.get('Exercise Name') or row.get('Skill / Action') or row.get('Exercise')
                desc = row.get('Specific Execution / Detail') or row.get('Equipment / Focus') or row.get('Thrower/Fielder Mechanics') or row.get('Description')
                cat = row.get('Category') or row.get('Type') or "General"
                
                if pd.notnull(name):
                    vault[sport_name].append({
                        "ex": str(name),
                        "cat": str(cat),
                        "sets": str(row.get('Sets', '3')),
                        "base": str(row.get('Reps/Dist.')) or str(row.get('Base', '10')),
                        "unit": str(row.get('Unit', 'reps')),
                        "rest": str(row.get('Rest', '60s')),
                        "time_goal": str(row.get('Goal', 'N/A')),
                        "desc": str(desc) if pd.notnull(desc) else "No description provided.",
                        "focus": str(row.get('Primary Focus', 'Performance'))
                    })
        except Exception as e:
            # This helps identify if it's a 404 or a data error
            st.sidebar.warning(f"⚠️ {sport_name} failed. Check spaces in filename.")
            
    return vault

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:#F8FAFC; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#000000; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#1E293B; margin:0; font-weight:bold;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    
    # Load data
    vault = load_vault_from_csv()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Sport Database", sport_options)
    num_drills = st.slider("Drills per Session", 1, 15, 5)
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            pool = vault[sport_choice]
            sample_size = min(len(pool), num_drills)
            st.session_state.current_session = random.sample(pool, sample_size)
            st.session_state.active_sport = sport_choice
        else:
            st.error("Could not find drills for this selection.")

# --- 4. MAIN DISPLAY ---
if st.session_state.current_session:
    st.title(f"🚀 {st.session_state.active_sport} Training ({difficulty})")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"DRILL {i+1}: {drill['ex']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Work", f"{drill['sets']} x {drill['base']} {drill['unit']}")
            c2.metric("Rest", drill['rest'])
            c3.metric("Goal", drill['time_goal'])
            
            st.markdown(f"**Execution:** {drill['desc']}")
            st.caption(f"Focus: {drill['focus']}")
            st.checkbox("Drill Complete", key=f"drill_{i}")
else:
    st.info("Pick a database and click 'Generate' to load your workout.")

# --- STYLING ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    [data-testid="stExpander"] { border: 1px solid #3B82F6; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)
