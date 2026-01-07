import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# ==================================================
# 1. APP CONFIG & SESSION STATE
# ==================================================
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if "current_session" not in st.session_state:
    st.session_state.current_session = None

if "archives" not in st.session_state:
    st.session_state.archives = []

if "view_archive_index" not in st.session_state:
    st.session_state.view_archive_index = None

if "set_counts" not in st.session_state:
    st.session_state.set_counts = {}

if "workout_finished" not in st.session_state:
    st.session_state.workout_finished = False

if "timers" not in st.session_state:
    st.session_state.timers = {}

if "stopwatches" not in st.session_state:
    st.session_state.stopwatches = {}

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete",
        "age": 17,
        "weight": 180,
        "goal_weight": 190,
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }

def get_now_est():
    return datetime.now(pytz.timezone("US/Eastern"))

# ==================================================
# 2. SIDEBAR
# ==================================================
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)

    st.divider()
    st.header("📂 WORKOUT HISTORY")

    if st.session_state.archives:
        names = [f"{a['date']} - {a['sport']}" for a in st.session_state.archives]
        choice = st.selectbox("View session:", ["Current / New"] + names)

        if choice != "Current / New":
            st.session_state.view_archive_index = names.index(choice)
        else:
            st.session_state.view_archive_index = None
    else:
        st.caption("No archived workouts yet")

    st.divider()
    st.header("👤 ATHLETE PROFILE")

    with st.expander("Edit Profile"):
        p = st.session_state.user_profile
        p["name"] = st.text_input("Name", p["name"]_
