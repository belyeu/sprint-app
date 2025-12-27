import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz  # Ensure this is in your requirements.txt

# --- 1. EST Time Logic ---
def get_est_time():
    # Use 'US/Eastern' to automatically handle Daylight Savings
    est_tz = pytz.timezone('US/Eastern')
    return datetime.now(est_tz)

# --- 2. High-Visibility Theme Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Initialize Session State
if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'session_saved' not in st.session_state: 
    st.session_state.session_saved = False

# Sidebar Display Settings
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

# CSS Variables for Light/Dark Mode Contrast
if dark_mode:
    bg_color, text_color, accent_color = "#0F172A", "#FFFFFF", "#3B82F6"
    header_bg, card_bg = "#1E293B", "#1E293B"
else:
    # High-contrast Light Mode to prevent iPhone "Graying Out"
    bg_color, text_color, accent_color = "#FFFFFF", "#000000", "#1E40AF"
    header_bg, card_bg = "#F1F5F9", "#F8FAFC"

st.markdown(f"""
    <style>
    /* Force high-visibility text on iPhone Safari */
    .stApp {{ background-color: {bg_color} !important; }}
    
    h1, h2, h3, p, span, label, div, li {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        opacity: 1 !important;
    }}

    /* Specific fix for checkbox labels and inputs that turn gray on mobile */
    .stCheckbox label p, .stTextInput label p {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}

    .drill-header {{
        font-size: 20px !important; font-weight: 800 !important; 
        color: {accent_color} !important; -webkit-text-fill-color: {accent_color} !important;
        background-color: {header_bg}; border-left: 8px solid {accent_color};
        padding: 10px; border-radius: 0 8px 8px 0; margin-top: 20px;
    }}

    .stat-label {{ font-size: 12px !important; font-weight: 800 !important; color: {accent_color} !important; }}
    .stat-value {{ font-size: 28px !important; font-weight: 900 !important; }}
    
    .stButton>button {{ 
        background-color: {accent_color} !important; color: white !important; 
        -webkit-text-fill-color: white !important; border-radius: 8px !important; 
        font-weight: 700 !important; height: 50px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. App Header with EST Clock ---
est_now = get_est_time()
st.markdown(f"### 📅 {est_now.strftime('%A, %b %d')} | 🕒 {est_now.strftime('%I:%M %p')} EST")
st.title("Pro-Athlete Daily Log")

# --- 4. Workout logic (Example: Basketball) ---
drills = [
    {"ex": "POUND SERIES", "desc": "Stationary dribbling, max force.", "sets": 3, "base": 60, "unit": "sec", "rest": 30},
    {"ex": "MIKAN SERIES", "desc": "Continuous layups, alternating hands.", "sets": 4, "base": 20, "unit": "reps", "rest": 45}
]

for i, item in enumerate(drills):
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    st.write(item["desc"])
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"COMPLETE SET", key=f"btn_{i}", use_container_width=True):
            st.toast(f"Set {i+1} logged!")
    with c2:
        if st.button(f"REST TIMER", key=f"rst_{i}", use_container_width=True):
            ph = st.empty()
            for t in range(item['rest'], -1, -1):
                ph.metric("Rest Remaining", f"{t}s")
                time.sleep(1)
            ph.empty()

    # Evaluation checkboxes (Fixed for iPhone visibility)
    st.checkbox("Perfect Form", key=f"form_{i}")
    st.text_input("Performance Notes", key=f"note_{i}", placeholder="e.g., Felt explosive today")

st.divider()

if st.button("💾 SAVE SESSION", use_container_width=True):
    st.balloons()
    st.success(f"Workout Saved at {get_est_time().strftime('%I:%M %p')} EST")
