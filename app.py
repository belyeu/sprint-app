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

# --- 2. DYNAMIC CSV LOADER ---
def load_vault_from_csv():
    # Use raw string or forward slashes for the path to handle spaces and slashes correctly
    file_path = "sprint-app/track drills - create table of all exercises.csv"
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Group exercises by Sport/Category column
        # Ensure your CSV has a 'Sport' column (or adjust the column name below)
        vault = {}
        sports = df['Sport'].unique()
        
        for sport in sports:
            sport_df = df[df['Sport'] == sport]
            vault[sport] = []
            for _, row in sport_df.iterrows():
                vault[sport].append({
                    "ex": row['Exercise'],
                    "sets": int(row['Sets']),
                    "base": int(row['Base']),
                    "unit": row['Unit'],
                    "rest": int(row['Rest']),
                    "time_goal": str(row['Goal']),
                    "desc": row.get('Description', 'No description provided.'),
                    "focus": str(row.get('Focus', 'Focus')).split(',') # Assumes comma-separated focus points
                })
        return vault
    except FileNotFoundError:
        st.error(f"⚠️ CSV not found at: {file_path}")
        return {}
    except Exception as e:
        st.error(f"⚠️ Error loading CSV: {e}")
        return {}

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
    
    # Load data from CSV
    vault = load_vault_from_csv()
    sport_options = list(vault.keys()) if vault else ["No Data Found"]
    
    sport_choice = st.selectbox("Sport Database", sport_options)
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.divider()
    if st.button("🔄 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = None

# --- [UI AND CSS REMAINS THE SAME AS PREVIOUS VERSION] ---
# (Apply the same CSS and loop logic as provided in the previous production-ready app)
