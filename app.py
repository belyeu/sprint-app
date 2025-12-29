import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. APP CONFIG & THEME TOGGLE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Persistent Title at the very top
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

# Sidebar Dark Mode Toggle
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)

# --- 2. UNIVERSAL RESPONSIVE CSS ---
if dark_mode:
    primary_bg = "#0F172A"
    card_bg = "#1E293B"
    text_color = "#F8FAFC"
    border_color = "#3B82F6"
    metric_bg = "rgba(59, 130, 246, 0.1)"
else:
    primary_bg = "#FFFFFF"
    card_bg = "#F1F5F9"
    text_color = "#1E293B"
    border_color = "#CBD5E1"
    metric_bg = "#E2E8F0"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{
        background-color: {primary_bg};
        color: {text_color};
    }}

    /* Expander / Drill Cards */
    [data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        margin-bottom: 15px !important;
    }}

    /* Metrics Styling */
    [data-testid="stMetricValue"] {{
        color: #3B82F6 !important;
        font-weight: 800 !important;
    }}
    
    div[data-testid="stMetric"] {{
        background-color: {metric_bg};
        padding: 15px;
        border-radius: 10px;
    }}

    /* Responsive adjustments for mobile */
    @media (max-width: 640px) {{
        [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
        h1 {{ font-size: 1.6rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

if 'current_session' not in st.session_state:
    st.session_state.current_session = None

# --- 3. DYNAMIC GITHUB CSV LOADER ---
def load_vault_from_csv():
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
                vault[sport_name].append({
                    "ex": str(row.get('Exercise') or row.get('Drill / Move Name') or "Unknown"),
                    "desc": str(row.get('Detailed Description') or row.get('Description') or "No details."),
                    "sets": str(row.get('Sets', '3')),
                    "reps": str(row.get('Reps/Dist.') or row.get('Base', '10')),
                    "focus": str(row.get('Primary Focus', 'Core Performance')),
                    "stars": str(row.get('Fitness Stars', '⭐⭐⭐')),
                    "rest": str(row.get('Rest', '60s'))
                })
        except Exception:
            st.sidebar.error(f"⚠️ {sport_name} Unavailable")
    return vault

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{card_bg}; padding:15px; border-radius:10px; border: 1px solid #3B82F6; text-align:center;">
        <h2 style="color:#3B82F6; margin:0; font-size:22px;">{get_now_est().strftime('%I:%M %p')}</h2>
        <p style="margin:0; opacity:0.8;">{get_now_est().strftime('%A, %b %d')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("🏟️ SESSION CONTROL")
    
    vault = load_vault_from_csv()
    sport_options = list(vault.keys()) if vault else ["General"]
    
    # Defaulting to General
    default_idx = sport_options.index("General") if "General" in sport_options else 0
    sport_choice = st.selectbox("Sport Database", sport_options, index=default_idx)
    
    # Range 12-15 as requested
    num_drills = st.slider("Exercises per Session", 12, 15, 13)
    
    st.divider()
    if st.button("🚀 GENERATE SESSION", use_container_width=True):
        if sport_choice in vault and vault[sport_choice]:
            pool = vault[sport_choice]
            count = min(len(pool), num_drills)
            st.session_state.current_session = random.sample(pool, count)
            st.session_state.active_sport = sport_choice

# --- 5. MAIN INTERFACE ---
if st.session_state.current_session:
    st.subheader(f"⚡ Current Training: {st.session_state.active_sport}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']}", expanded=(i == 0)):
            # Row 1: Key Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Work", f"{drill['sets']} x {drill['reps']}")
            m2.metric("Rating", drill['stars'])
            m3.metric("Rest", drill['rest'])
            
            # Row 2: Content
            st.markdown(f"**🎯 Focus:** {drill['focus']}")
            st.markdown(f"**📝 Instructions:** {drill['desc']}")
            
            # Checkbox for mobile tracking
            st.checkbox("Done", key=f"complete_{i}")
else:
    st.info("👋 Select a sport and generate a session (12-15 exercises) to begin your workout.")
