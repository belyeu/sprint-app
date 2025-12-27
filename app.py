import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME LOGIC ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    """Returns current time in US/Eastern timezone."""
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0

# --- 2. DYNAMIC THEME & IPHONE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    btn_txt = "#FFFFFF"
else:
    # High-contrast Light Mode for iPhone Safari
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    btn_txt = "#FFFFFF" 

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{ background-color: {bg} !important; }}
    
    /* Force Safari iPhone Text Visibility (Black in Light, White in Dark) */
    h1, h2, h3, p, span, label, li, .stMarkdown p {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
        font-weight: 500;
    }}

    /* Aggressive Button Styling for iPhone Light Mode */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        width: 100% !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Force Button Text to White on iPhone */
    div.stButton > button div p, 
    div.stButton > button p,
    div.stButton > button span {{
        color: {btn_txt} !important;
        -webkit-text-fill-color: {btn_txt} !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        text-transform: uppercase;
        opacity: 1 !important;
    }}

    /* Expander & Input Boxes */
    [data-testid="stExpander"], input, textarea {{
        background-color: {header} !important;
        border: 2px solid {accent} !important;
        border-radius: 10px !important;
        color: {text} !important;
    }}

    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; 
        color: {accent} !important; -webkit-text-fill-color: {accent} !important;
        background-color: {header}; border-left: 10px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
    }}

    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent}; 
        background-color: {header}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION & STATS ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    <p style="margin:0; font-size:14px;">{now_est.strftime('%A, %b %d')}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "Session History"])
sport_choice = st.sidebar.selectbox("Sport", ["Basketball", "Track", "Softball", "General Workout"])

# --- 4. WORKOUT PLAN PAGE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} Dashboard")
    
    # Drill Data Structure
    drills = [
        {"ex": "POUND SERIES", "desc": "Stationary dribbling, max force.", "rest": 30},
        {"ex": "MIKAN SERIES", "desc": "Continuous layups, alternating hands.", "rest": 45},
        {"ex": "FIGURE 8", "desc": "Ball handling through legs.", "rest": 30}
    ]

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"SET COMPLETE ✅", key=f"d_{i}"):
                st.toast(f"Logged: {item['ex']}")
        with c2:
            if st.button(f"START REST ⏱️", key=f"r_{i}"):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()
                st.audio("https://www.soundjay.com/buttons/beep-01a.mp3")

        # Evaluation & Notes
        st.checkbox("Perfect Form / High Intensity", key=f"f_{i}")
        st.text_input("Performance Notes", key=f"n_{i}", placeholder="How did this set feel?")
        
        with st.expander("🎥 DEMO & VIDEO UPLOAD"):
            st.write("Review mechanics and log your progress.")
            st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"u_{i}")

    st.divider()
    if st.button("💾 SAVE FULL WORKOUT"):
        # Save to History with EST timestamp
        timestamp = get_now_est().strftime("%b %d, %Y | %I:%M %p")
        st.session_state.history.append({
            "date": timestamp, 
            "sport": sport_choice,
            "status": "Completed"
        })
        st.session_state.streak += 1
        st.balloons()
        st.success(f"Session Saved Successfully at {timestamp} EST")

# --- 5. SESSION HISTORY PAGE ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No saved sessions yet. Start training to build your history!")
    else:
        # Display history in reverse chronological order
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:12px; border:1px solid {accent}; background-color:{header}; margin-bottom:12px;">
                <p style="margin:0; font-weight:900; font-size:18px; color:{accent} !important;">{log['sport']} Session</p>
                <p style="margin:0; font-size:14px; font-weight:600;">Logged: {log['date']} EST</p>
                <p style="margin:5px 0 0 0; font-size:12px; text-transform:uppercase; color:green !important;">● {log['status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("Clear All History"):
            st.session_state.history = []
            st.rerun()
