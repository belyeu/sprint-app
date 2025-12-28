import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_github():
    # Replace [USERNAME] and [REPO] with your actual GitHub details
    # Example: "https://raw.githubusercontent.com/johndoe/my-drills/main/"
    base_url = "https://raw.githubusercontent.com/[USERNAME]/[REPO]/main/"
    
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
            df = pd.read_csv(url)
            
            # Standardization: Ensure columns match the expected app keys
            # Even if headers vary slightly, we map them here
            vault[sport] = []
            for _, row in df.iterrows():
                # Handling different possible column naming conventions in your CSVs
                vault[sport].append({
                    "ex": row.get('Exercise') or row.get('Exercise Name') or row.get('Drill / Move Name'),
                    "sets": int(row.get('Sets', 3)),
                    "base": int(row.get('Base') or row.get('Reps/Dist.', 10)),
                    "unit": row.get('Unit', 'reps'),
                    "rest": int(row.get('Rest', 60)),
                    "time_goal": str(row.get('Goal', 'N/A')),
                    "desc": row.get('Detailed Description') or row.get('Specific Execution / Detail') or 'No description.',
                    "focus": str(row.get('Primary Focus', 'Focus')).split(',')
                })
        except Exception as e:
            st.sidebar.warning(f"Could not load {sport}: {e}")
            
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
    
    # Load data from Github
    vault = load_vault_from_github()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Sport Database", sport_options)
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        if sport_choice in vault:
            # Select 5 random exercises from the chosen sport CSV
            exercises = random.sample(vault[sport_choice], min(len(vault[sport_choice]), 5))
            st.session_state.current_session = exercises
        else:
            st.error("Please select a valid sport database.")

# --- 4. MAIN DISPLAY ---
if st.session_state.current_session:
    st.title(f"🚀 {sport_choice} Session: {difficulty}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"Drill {i+1}: {drill['ex']}", expanded=True):
            col1, col2, col3 = columns = st.columns(3)
            col1.metric("Work", f"{drill['sets']} x {drill['base']} {drill['unit']}")
            col2.metric("Rest", f"{drill['rest']}s")
            col3.metric("Goal", drill['time_goal'])
            
            st.write(f"**Description:** {drill['desc']}")
            st.write(f"**Focus:** {', '.join(drill['focus'])}")
else:
    st.info("Select a Sport and click 'Generate New Session' in the sidebar to begin.")
