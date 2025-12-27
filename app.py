import streamlit as st
import pandas as pd
import time

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
    .coach-eval {
        background-color: #004d26; border: 2px dashed #FFD700;
        padding: 20px; border-radius: 10px; margin-top: 20px;
    }
    .stButton>button { 
        background-color: #FFD700; color: #013220; border-radius: 10px; 
        font-weight: bold; border: 2px solid #DAA520; width: 100%; height: 60px; font-size: 22px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_workout_template():
    return [
        {"ex": "POUND SERIES", "base_reps": 30, "sets": 4, "inc": 5, "unit": "sec", "pro_bench": 240, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
        {"ex": "MIKAN SERIES", "base_reps": 25, "sets": 4, "inc": 5, "unit": "makes", "pro_bench": 120, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"}
    ]

st.header("🔥 ELITE SELF-CORRECTION HUB")
drills = get_workout_template()

for i, item in enumerate(drills):
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("🎥 VIDEO ANALYSIS & COACH'S EVAL", expanded=True):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("**PRO MODEL**")
            st.video(item['vid'])
        with col_v2:
            st.markdown("**YOUR CLIP**")
            user_url = st.text_input("Paste Link:", key=f"vid_{i}")
            if user_url:
                st.video(user_url)

        # --- Coach's Evaluation Section ---
        st.markdown('<div class="coach-eval">', unsafe_allow_html=True)
        st.subheader("📋 COACH'S EVALUATION")
        q1 = st.checkbox("Was my posture/spine neutral throughout the movement?", key=f"q1_{i}")
        q2 = st.checkbox("Did I maintain game-speed intensity (no coasting)?", key=f"q2_{i}")
        q3 = st.checkbox("Did my mechanics match the pro demo (elbows/feet)?", key=f"q3_{i}")
        
        notes = st.text_area("What is ONE specific adjustment for the next set?", key=f"note_{i}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Logging
        c1, c2 = st.columns(2)
        with c1: st.number_input("Total Result", key=f"res_{i}")
        with c2: st.select_slider("RPE", options=range(1,11), value=8, key=f"rpe_{i}")

if st.button("💾 SAVE SESSION & EVALUATIONS"):
    st.balloons()
    st.success("Session data and self-evaluations archived for review.")
