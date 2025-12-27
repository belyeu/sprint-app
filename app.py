import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME LOGIC ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    """Returns current time in US/Eastern (EST/EDT) regardless of server location."""
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0

# --- 2. DYNAMIC THEME & IPHONE CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

# Theme Logic
if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
else:
    # High-contrast Light Mode optimized for iPhone Safari
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

# We strictly force white for button text to pop against the blue accent
btn_txt_white = "#FFFFFF"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{ background-color: {bg} !important; }}
    
    /* Force Global Text Visibility (No transparency for Safari) */
    h1, h2, h3, p, span, label, li {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
        font-weight: 500;
    }}

    /* AGGRESSIVE BUTTON OVERRIDE: Forces White Text on iPhone */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        width: 100% !important;
        border-radius: 12px !important;
    }}

    /* This targets every possible text container inside a Streamlit button */
    div.stButton > button p, 
    div.stButton > button span,
    div.stButton > button div,
    div.stButton > button label {{
        color: {btn_txt_white} !important;
        -webkit-text-fill-color: {btn_txt_white} !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        opacity: 1 !important;
        text-transform: uppercase;
    }}

    /* Expander & Input Boxes */
    [data-testid="stExpander"], input, textarea {{
        background-color: {header} !important;
        border: 2px solid {accent} !important;
        border-radius: 10px !important;
        color: {text} !important;
    }}

    /* Athlete Branding Styles */
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
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    <p style="margin:0; font-size:13px; font-weight:600;">{now_est.strftime('%A, %b %d')}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:11px; color:{accent}; font-weight:800;">STREAK</p>
    <p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "Session History"])
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])

# --- 4. WORKOUT PLAN PAGE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} Session")
    
    # Drill Data (Example template)
    drills = [
        {"ex": "POUND SERIES", "desc": "Stationary dribbling with maximum force.", "rest": 30},
        {"ex": "MIKAN SERIES", "desc": "Continuous layups, alternating hands for touch.", "rest": 45}
    ]

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"SET DONE ✅", key=f"done_{i}"):
                st.toast(f"Logged: {item['ex']}")
        with col2:
            if st.button(f"REST ⏱️", key=f"rest_{i}"):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:44px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()
                st.toast("Rest Over! Back to work.")

        st.checkbox("Perfect Form / High Intensity", key=f"check_{i}")
        st.text_input("Performance Notes", key=f"note_{i}", placeholder="How did this set feel?")
        
        with st.expander("🎥 DEMO & UPLOAD"):
            st.file_uploader("Upload Session Clip", type=["mp4", "mov"], key=f"upload_{i}")

    st.divider()
    
    # Save/Reset Logic
    s1, s2 = st.columns(2)
    with s1:
        if st.button("💾 SAVE WORKOUT"):
            timestamp = get_now_est().strftime("%b %d, %Y | %I:%M %p")
            st.session_state.history.append({"date": timestamp, "sport": sport_choice})
            st.session_state.streak += 1
            st.balloons()
            st.success(f"Session Saved at {timestamp} EST")
    with s2:
        if st.button("🔄 RESET SESSION"):
            st.rerun()

# --- 5. SESSION HISTORY PAGE ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No saved sessions yet. Time to get to work!")
    else:
        # Display logs from newest to oldest
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:12px; border:1px solid {accent}; background-color:{header}; margin-bottom:12px;">
                <p style="margin:0; font-weight:900; font-size:18px; color:{accent} !important;">{log['sport']} Session</p>
                <p style="margin:0; font-size:14px; font-weight:700;">{log['date']} EST</p>
                <p style="margin:5px 0 0 0; font-size:12px; color:green !important;">● COMPLETED</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("Clear All History"):
            st.session_state.history = []
            st.rerun()
