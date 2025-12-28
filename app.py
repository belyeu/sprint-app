import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. SETUP & PERSISTENCE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'history' not in st.session_state: st.session_state.history = []
if 'current_session' not in st.session_state: st.session_state.current_session = None

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_github():
    username = "belyeu"
    repo = "sprint-app"
    branch = "main"
    
    # Base URL for Raw GitHub content
    base_url = f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/"
    
    # Map display names to exact GitHub filenames (URL encoded)
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
            # Fetch the CSV
            df = pd.read_csv(url)
            
            vault[sport] = []
            for _, row in df.iterrows():
                # Helper to find data regardless of varying column names in your 4 files
                name = row.get('Drill / Move Name') or row.get('Exercise Name') or row.get('Skill / Action') or row.get('Exercise')
                desc = row.get('Specific Execution / Detail') or row.get('Equipment / Focus') or row.get('Thrower/Fielder Mechanics') or row.get('Description')
                
                # Append to vault if a name was found
                if pd.notnull(name):
                    vault[sport].append({
                        "ex": str(name),
                        "sets": str(row.get('Sets', '3')),
                        "base": str(row.get('Reps/Dist.', '10')),
                        "unit": str(row.get('Unit', 'reps')),
                        "rest": str(row.get('Rest', '60s')),
                        "time_goal": str(row.get('Goal', 'N/A')),
                        "desc": str(desc) if pd.notnull(desc) else "No additional details provided.",
                        "focus": str(row.get('Primary Focus', 'Performance'))
                    })
        except Exception as e:
            st.sidebar.error(f"⚠️ Error loading {sport}: Check if file exists in repo.")
            
    return vault

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:#F8FAFC; padding:20px; border-radius:15px; border: 2px solid #3B82F6; text-align:center; margin-bottom:25px;">
        <h1 style="color:#000000; margin:0; font-size:28px;">{get_now_est().strftime('%I:%M %p')}</h1>
        <p style="color:#1E293B; margin:0; font-weight:bold; letter-spacing:1px;">{get_now_est().strftime('%A, %b %d').upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    
    # Load data from Github
    vault = load_vault_from_github()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Select Database", sport_options)
    num_drills = st.slider("Number of Drills", 1, 10, 5)
    
    st.divider()
    if st.button("🔄 GENERATE SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            # Randomly select exercises based on slider
            count = min(len(vault[sport_choice]), num_drills)
            st.session_state.current_session = random.sample(vault[sport_choice], count)
        else:
            st.error("No data available for this selection.")

# --- 4. MAIN DISPLAY ---
if st.session_state.current_session:
    st.title(f"🚀 {sport_choice} Training Session")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"DRILL {i+1}: {drill['ex']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Work", f"{drill['sets']} x {drill['base']}")
            c2.metric("Rest", drill['rest'])
            c3.metric("Focus", drill['focus'])
            
            st.info(f"**Execution:** {drill['desc']}")
else:
    st.info("Select a database in the sidebar and click 'Generate Session' to begin.")
