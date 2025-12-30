import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["General", "Basketball", "Softball", "Track"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track"],
        default=["Gym"]
    )
    num_drills = st.slider("Exercises", 5, 20, 12)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F1F5F9"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
border_color = "#3B82F6" if dark_mode else "#CBD5E1"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    [data-testid="stExpander"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 12px !important; 
    }}
    .stat-box {{
        background: rgba(59, 130, 246, 0.1);
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADING (Updated for all fields) ---
def load_data(sport):
    urls = {
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/main/general.csv",
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/basketball%20drills%20-%20Sheet1.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/main/track%20drills%20-%20track.csv"
    }
    try:
        df = pd.read_csv(urls[sport])
        df.columns = [c.strip() for c in df.columns]
        
        data_list = []
        for _, row in df.iterrows():
            data_list.append({
                "ex": row.get('Exercise Name') or row.get('Exercise') or "Unknown Exercise",
                "env": row.get('Env.') or row.get('Location') or "Gym",
                "category": row.get('Category') or "Athleticism",
                "cns": row.get('CNS') or "Medium",
                "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist') or row.get('Reps/Dist.') or "N/A",
                "time": row.get('Time') or "N/A",
                "focus": row.get('Primary Focus') or "Performance",
                "stars": row.get('Stars') or row.get('Fitness Stars') or "⭐⭐⭐",
                "pre_req": row.get('Pre-Req') or "None",
                "hs_goals": row.get('HS Goals') or "Standard",
                "college_goals": row.get('College Goals') or "Elite",
                "desc": row.get('Description') or row.get('Detailed Description') or "No description.",
                "demo": row.get('Demo') or row.get('Video URL') or ""
            })
        return data_list
    except:
        return []

# --- 5. GENERATION LOGIC ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(sport_choice)
        filtered_pool = [d for d in pool if d['env'] in location_filter] or pool
        st.session_state.current_session = random.sample(filtered_pool, min(len(filtered_pool), num_drills))
        st.session_state.active_sport = sport_choice
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** | {drill['stars']}", expanded=(i==0)):
            # Field Layout
            col1, col2, col3 = st.columns([1.5, 1, 1.5])
            
            with col1:
                st.markdown(f"**📂 Category:** {drill['category']}")
                st.markdown(f"**🧠 CNS Load:** {drill['cns']}")
                st.markdown(f"**📍 Env:** {drill['env']}")
                st.markdown(f"**🎯 Focus:** {drill['focus']}")
                st.markdown(f"**⚠️ Pre-Req:** {drill['pre_req']}")

            with col2:
                st.markdown(f"**🔢 Sets:** {drill['sets']}")
                st.markdown(f"**🔄 Reps/Dist:** {drill['reps']}")
                st.markdown(f"**🕒 Time:** {drill['time']}")
                st.markdown(f"**🏫 HS Goal:** {drill['hs_goals']}")
                st.markdown(f"**🎓 College:** {drill['college_goals']}")

            with col3:
                st.info(f"**Description:** {drill['desc']}")
            
            st.divider()
            
            # Action Area
            a1, a2 = st.columns([1, 1])
            with a1:
                curr_sets = st.session_state.set_counts.get(i, 0)
                if st.button(f"Log Set ({curr_sets}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    if curr_sets < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if curr_sets >= drill['sets']:
                    st.success("Exercise Complete!")
                
                if drill['demo'] and "http" in str(drill['demo']):
                    st.video(drill['demo'])
                else:
                    st.caption("No video demo available.")

            with a2:
                # Timer Block
                st.markdown("#### ⏱️ Rest / Drill Timer")
                t_val = st.number_input("Seconds", 5, 300, 60, key=f"t_in_{i}")
                if st.button("Start Timer", key=f"t_btn_{i}"):
                    ph = st.empty()
                    for t in range(t_val, -1, -1):
                        ph.metric("Remaining", f"{t}s")
                        time.sleep(1)
                    st.balloons()

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.header("📝 Workout Summary")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'category', 'sets', 'focus']])
    if st.button("Start New"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("Select options in the sidebar and click 'Generate Workout'.")
