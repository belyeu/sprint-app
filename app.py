import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & THEMING ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Timezone Setup
def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize State
if 'history' not in st.session_state: st.session_state.history = []
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'monthly_count' not in st.session_state: st.session_state.monthly_count = 0

# Sidebar Settings
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

# Theme Logic
if dark_mode:
    bg, text, accent, header, card = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B", "#1E293B"
    input_txt = "#60A5FA"
else:
    # High-contrast Light Mode for iPhone Safari
    bg, text, accent, header, card = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9", "#F8FAFC"
    input_txt = "#000000"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    /* Force Safari iPhone Text Visibility */
    h1, h2, h3, p, span, label, li, .stMarkdown p {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
        font-weight: 500;
    }}

    /* Specific Fix for Inputs & Gray-out */
    input, textarea, [data-testid="stExpander"] {{
        background-color: {header} !important;
        color: {input_txt} !important;
        -webkit-text-fill-color: {input_txt} !important;
    }}

    [data-testid="stExpander"] {{
        border: 2px solid {accent} !important;
        border-radius: 12px !important;
    }}

    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
    }}

    .stButton>button {{ 
        background-color: {accent} !important; color: white !important; 
        -webkit-text-fill-color: white !important; font-weight: 800 !important; 
        height: 55px !important; border-radius: 10px !important;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent}; 
        background-color: {card}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR STATS ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    <p style="margin:0; font-size:14px;">{now_est.strftime('%A, %b %d')}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f'<div class="sidebar-card"><p style="color:{accent}; font-size:12px; margin:0;">STREAK</p><p style="font-size:24px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p></div>', unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "History & Progress"])
sport_choice = st.sidebar.selectbox("Sport", ["Basketball", "Track", "Softball", "General Workout"])

# --- 3. WORKOUT PLAN ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} Session")
    
    # Example Drill Logic (Simplified for demonstration)
    drills = [
        {"ex": "POUND SERIES", "desc": "Stationary dribbling, max force.", "rest": 30},
        {"ex": "MIKAN SERIES", "desc": "Continuous layups, alternating hands.", "rest": 45}
    ]

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"DONE ✅", key=f"d_{i}", use_container_width=True):
                st.toast(f"Set {i+1} logged!")
        with c2:
            if st.button(f"REST ⏱️", key=f"r_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:40px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

        st.checkbox("Perfect Form", key=f"f_{i}")
        st.text_input("Notes", key=f"n_{i}")
        
        with st.expander("🎥 DEMO & UPLOAD"):
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"u_{i}")

    st.divider()
    if st.button("💾 SAVE WORKOUT", use_container_width=True):
        timestamp = get_now_est().strftime("%Y-%m-%d %I:%M %p")
        st.session_state.history.append({"date": timestamp, "sport": sport_choice})
        st.session_state.streak += 1
        st.balloons()
        st.success(f"Workout Saved at {timestamp} EST")

# --- 4. HISTORY & PROGRESS ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No workouts saved yet. Get to work!")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:10px; border-left:5px solid {accent}; background-color:{header}; margin-bottom:10px;">
                <p style="margin:0; font-weight:800;">{log['sport']} Session</p>
                <p style="margin:0; font-size:14px; opacity:0.8;">{log['date']} EST</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
