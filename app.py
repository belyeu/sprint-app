import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME LOGIC ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

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
    # High-contrast Light Mode
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"

# We force white for button text specifically
btn_txt_color = "#FFFFFF"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{ background-color: {bg} !important; }}
    
    /* Force Global Text Visibility */
    h1, h2, h3, p, span, label, li {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
    }}

    /* THE FIX: Target all buttons and their internal text 
       This forces WHITE text on the blue background for iPhone Safari
    */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        width: 100% !important;
        border-radius: 12px !important;
    }}

    /* Target the specific paragraph and span tags Streamlit uses inside buttons */
    div.stButton > button p, 
    div.stButton > button span,
    div.stButton > button div {{
        color: {btn_txt_color} !important;
        -webkit-text-fill-color: {btn_txt_color} !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        opacity: 1 !important;
    }}

    /* Reset/Secondary Button logic: If you want Reset to be a different color, 
       you can change the hex below, but text will still be white. */
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

# --- 3. SIDEBAR NAVIGATION ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "Session History"])
sport_choice = st.sidebar.selectbox("Sport", ["Basketball", "Track", "Softball", "General Workout"])

# --- 4. WORKOUT PLAN PAGE ---
if app_mode == "Workout Plan":
    st.title(f"{sport_choice} Session")
    
    # Example Drill
    st.markdown(f'<div class="drill-header">1. MAIN DRILL</div>', unsafe_allow_html=True)
    st.write("Focus on explosive movements and core stability.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("DONE ✅", key="done_1"):
            st.toast("Set logged!")
    with col2:
        if st.button("RESET 🔄", key="reset_1"):
            st.rerun()

    st.divider()
    if st.button("💾 SAVE FULL WORKOUT"):
        timestamp = get_now_est().strftime("%b %d, %I:%M %p")
        st.session_state.history.append({"date": timestamp, "sport": sport_choice})
        st.session_state.streak += 1
        st.balloons()
        st.success(f"Session Saved at {timestamp} EST")

# --- 5. SESSION HISTORY PAGE ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No saved sessions yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:12px; border:1px solid {accent}; background-color:{header}; margin-bottom:12px;">
                <p style="margin:0; font-weight:900; font-size:18px; color:{accent} !important;">{log['sport']} Session</p>
                <p style="margin:0; font-size:14px; font-weight:600;">Logged: {log['date']} EST</p>
            </div>
            """, unsafe_allow_html=True)
