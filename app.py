import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. SETUP & THEME ---
st.set_page_config(
    page_title="Pro-Athlete Tracker", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Universal Dark Mode & Mobile Responsive CSS
st.markdown("""
    <style>
    /* Global Styles */
    :root {
        --primary-blue: #3B82F6;
        --bg-dark: #0F172A;
        --card-dark: #1E293B;
        --text-main: #F8FAFC;
    }

    /* Target all platforms (iOS/Android/Desktop) */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-main);
    }

    /* Drill Cards */
    [data-testid="stExpander"] {
        background-color: var(--card-dark) !important;
        border: 1px solid var(--primary-blue) !important;
        border-radius: 12px !important;
        margin-bottom: 15px !important;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: var(--primary-blue) !important;
        font-weight: bold !important;
    }
    
    .stMetric {
        background-color: rgba(59, 130, 246, 0.1);
        padding: 10px;
        border-radius: 8px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
    }
    
    /* Responsive font sizing for mobile */
    @media (max-width: 640px) {
        .stMetricValue { font-size: 1.5rem !important; }
        h1 { font-size: 1.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'current_session' not in st.session_state:
    st.session_state.current_session = None

# --- 2. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_csv():
    # Finalized verified paths
    files = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    
    vault = {}

    for sport_name, url in files.items():
        try:
            df = pd.read_csv(url)
            vault[sport_name] = []
            
            for _, row in df.iterrows():
                # Mapping specifically requested fields
                # fallback values ensure the app doesn't crash if a row is empty
                vault[sport_name].append({
                    "ex": str(row.get('Exercise') or row.get('Drill / Move Name') or "Unknown Exercise"),
                    "desc": str(row.get('Detailed Description') or row.get('Description') or "No description provided."),
                    "sets": str(row.get('Sets', '3')),
                    "reps": str(row.get('Reps/Dist.') or row.get('Base', '10')),
                    "focus": str(row.get('Primary Focus', 'Performance')),
                    "stars": str(row.get('Fitness Stars', '⭐⭐⭐')),
                    "unit": str(row.get('Unit', 'reps')),
                    "rest": str(row.get('Rest', '60s'))
                })
        except Exception:
            st.sidebar.error(f"❌ {sport_name} database unavailable.")
            
    return vault

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:#1E293B; padding:15px; border-radius:10px; border: 1px solid #3B82F6; text-align:center;">
        <h2 style="color:#F8FAFC; margin:0; font-size:24px;">{get_now_est().strftime('%I:%M %p')}</h2>
        <p style="color:#94A3B8; margin:0;">{get_now_est().strftime('%A, %b %d')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION GENERATOR")
    
    vault = load_vault_from_csv()
    sport_options = list(vault.keys()) if vault else ["General"]
    
    # "General" set as default database
    default_index = sport_options.index("General") if "General" in sport_options else 0
    sport_choice = st.selectbox("Select Database", sport_options, index=default_index)
    
    # Minimum requirement of 12-15 exercises
    num_drills = st.slider("Exercises per Session", 12, 18, 14)
    
    st.divider()
    if st.button("🚀 GENERATE PRO SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            pool = vault[sport_choice]
            # Handle if the database is smaller than requested number
            actual_count = min(len(pool), num_drills)
            st.session_state.current_session = random.sample(pool, actual_count)
            st.session_state.active_sport = sport_choice
        else:
            st.error("Database empty or not found.")

# --- 4. MAIN INTERFACE ---
if st.session_state.current_session:
    st.title(f"🔥 {st.session_state.active_sport} Session")
    st.caption(f"Target: {len(st.session_state.current_session)} High-Intensity Exercises")

    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i == 0)):
            # Row 1: Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Work", f"{drill['sets']} x {drill['reps']}")
            c2.metric("Difficulty", drill['stars'])
            c3.metric("Rest", drill['rest'])
            
            # Row 2: Detailed Info
            st.markdown(f"**🎯 Primary Focus:** {drill['focus']}")
            st.markdown(f"**📝 Instructions:** {drill['desc']}")
            
            # Interactive Finish
            st.checkbox("Exercise Complete", key=f"drill_{i}")

else:
    st.info("👋 Welcome! Use the sidebar to generate a 12-15 exercise session. Defaulting to 'General' database.")
