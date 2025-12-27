import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & EST TIME ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# Initialize State
if 'history' not in st.session_state: st.session_state.history = []
if 'streak' not in st.session_state: st.session_state.streak = 0

# Sidebar Settings
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=False)

# Theme Logic
if dark_mode:
    bg, text, accent, header = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    btn_txt = "#FFFFFF"
else:
    # High-contrast Light Mode
    bg, text, accent, header = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    btn_txt = "#FFFFFF" # Forced White

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    /* Global Text Visibility */
    h1, h2, h3, p, span, label, li {{
        color: {text} !important;
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
    }}

    /* AGGRESSIVE BUTTON FIX FOR IPHONE LIGHT MODE */
    div.stButton > button {{
        background-color: {accent} !important;
        border: none !important;
        height: 55px !important;
        width: 100% !important;
        border-radius: 12px !important;
    }}

    /* Target the text inside the button specifically */
    div.stButton > button div p, 
    div.stButton > button p,
    div.stButton > button span {{
        color: {btn_txt} !important;
        -webkit-text-fill-color: {btn_txt} !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        opacity: 1 !important;
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

# --- 2. SIDEBAR ---
now_est = get_now_est()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">CURRENT TIME (EST)</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Navigate", ["Workout Plan", "History"])

# --- 3. WORKOUT PLAN ---
if app_mode == "Workout Plan":
    st.title("Pro-Athlete Session")
    
    drills = [
        {"ex": "POUND SERIES", "desc": "Stationary dribbling, max force.", "rest": 30},
        {"ex": "MIKAN SERIES", "desc": "Continuous layups, alternating hands.", "rest": 45}
    ]

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"DONE ✅", key=f"d_{i}"):
                st.toast(f"Set {i+1} logged!")
        with c2:
            if st.button(f"REST ⏱️", key=f"r_{i}"):
                ph = st.empty()
                for t in range(item['rest'], -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:40px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

    st.divider()
    if st.button("💾 SAVE WORKOUT"):
        timestamp = get_now_est().strftime("%b %d, %I:%M %p")
        st.session_state.history.append({"date": timestamp, "type": "Full Session"})
        st.session_state.streak += 1
        st.balloons()
        st.success(f"Workout Saved at {timestamp} EST")

# --- 4. HISTORY ---
else:
    st.title("📊 Session History")
    if not st.session_state.history:
        st.info("No saved sessions yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="padding:15px; border-radius:10px; border:1px solid {accent}; background-color:{header}; margin-bottom:10px;">
                <p style="margin:0; font-weight:800;">{log['type']}</p>
                <p style="margin:0; font-size:14px;">{log['date']} EST</p>
            </div>
            """, unsafe_allow_html=True)
