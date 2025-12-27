import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

# --- Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #013220; color: #ffffff; }
    .drill-header {
        font-size: 34px !important; font-weight: 900 !important; color: #FFD700 !important;
        text-transform: uppercase; margin-top: 30px; font-family: 'Arial Black', sans-serif;
        border-left: 10px solid #FFD700; padding-left: 20px;
    }
    .video-comparison {
        background-color: #1a1a1a; padding: 15px; border-radius: 10px;
        border: 1px solid #FFD700; margin-top: 10px;
    }
    .stButton>button { 
        background-color: #FFD700; color: #013220; border-radius: 10px; 
        font-weight: bold; border: 2px solid #DAA520; width: 100%; height: 60px; font-size: 22px;
    }
    .stMetric { background-color: #004d26; padding: 20px; border-radius: 12px; border: 3px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State for Personal Videos ---
if 'personal_vids' not in st.session_state:
    st.session_state.personal_vids = {}

def get_workout_template(sport):
    return [
        {"ex": "POUND SERIES", "base_reps": 30, "sets": 4, "inc": 5, "unit": "sec", "rest": 30, "pro_bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
        {"ex": "MIKAN SERIES", "base_reps": 25, "sets": 4, "inc": 5, "unit": "makes", "rest": 60, "pro_bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"}
    ]

st.header("🔥 PRO-LEVEL FORM ANALYZER")
drills = get_workout_template("Basketball")

for i, item in enumerate(drills):
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("🎥 FORM COMPARISON & LOGGING", expanded=True):
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.markdown("**PRO DEMONSTRATION**")
            st.video(item['vid'])
            st.caption("Focus on: Elbow alignment and footwork rhythm.")
            
        with col_v2:
            st.markdown("**YOUR TECHNIQUE**")
            user_url = st.text_input("Paste your video link (Drive/YT/Hudl):", key=f"vid_input_{i}")
            if user_url:
                st.session_state.personal_vids[item['ex']] = user_url
                try:
                    st.video(user_url)
                except:
                    st.error("Make sure your link is public or shared.")
            else:
                st.info("Upload your rep to see a side-by-side comparison.")

        st.divider()
        
        # Logging Section
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            st.metric("Total Goal", f"{item['base_reps'] * item['sets']} {item['unit']}")
        with c2:
            st.number_input("Logged Result", key=f"log_{i}")
        with c3:
            st.select_slider("Intensity", options=range(1, 11), value=8, key=f"rpe_{i}")

if st.button("💾 SAVE SESSION & VIDEO LINKS"):
    st.success("Session and video vault updated!")
