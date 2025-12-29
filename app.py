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
if 'workout_log' not in st.session_state:
    st.session_state.workout_log = []

# --- 2. SIDEBAR: APPEARANCE & FILTERS ---
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
        "Facility Location", 
        ["Gym", "Field", "Cages", "Weight Room", "Track"],
        default=["Gym"]
    )
    num_drills = st.slider("Exercises", 12, 15, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_map = {"Low": 25, "Moderate": 50, "High": 75, "Elite": 100}
    st.progress(intensity_map[effort])

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
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADING ---
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
            name = row.get('Exercise') or row.get('Exercise Name') or row.get('Drill / Move Name') or "Unknown Exercise"
            data_list.append({
                "ex": name,
                "desc": row.get('Detailed Description') or row.get('Description') or "No details.",
                "focus": row.get('Primary Focus') or "Core Performance",
                "stars": row.get('Fitness Stars') or "⭐⭐⭐",
                "sets": int(row.get('Sets', 3)) if str(row.get('Sets')).isdigit() else 3,
                "reps": row.get('Reps/Dist.') or "10",
                "rest": row.get('Rest') or "60s",
                "video": row.get('Video URL') or ""
            })
        return data_list
    except:
        return []

# --- 5. GENERATION LOGIC ---
with st.sidebar:
    st.divider()
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        pool = load_data(sport_choice)
        if pool:
            st.session_state.current_session = random.sample(pool, min(len(pool), num_drills))
            st.session_state.active_sport = sport_choice
            st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
            st.session_state.workout_log = []

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

# Dashboard Goals
g1, g2 = st.columns(2)
g1.metric("High School Goal", st.session_state.user_profile["hs_goal"])
g2.metric("College Goal", st.session_state.user_profile["college_goal"])

if st.session_state.current_session:
    st.subheader(f"⚡ {st.session_state.active_sport} Session | Location: {', '.join(location_filter)}")
    
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE {i+1}: {drill['ex']} {drill['stars']}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🎯 Focus:** {drill['focus']}")
                st.markdown(f"**📝 Description:** {drill['desc']}")
                st.write(f"**Goal:** {drill['sets']} Sets x {drill['reps']}")
                
                # 1-BUTTON COUNTER
                curr_sets = st.session_state.set_counts.get(i, 0)
                if st.button(f"Log Set ({curr_sets}/{drill['sets']})", key=f"btn_{i}"):
                    if curr_sets < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                if curr_sets >= drill['sets']:
                    st.success("✅ Exercise Complete!")

            with col2:
                # EXERCISE & REST TIMERS
                t1, t2 = st.columns(2)
                
                with t1:
                    st.markdown("#### 🏃 Drill Timer")
                    work_time = st.number_input("Seconds", 5, 300, 30, key=f"work_val_{i}")
                    if st.button(f"Start Drill", key=f"work_btn_{i}"):
                        ph = st.empty()
                        for t in range(work_time, -1, -1):
                            ph.metric("Go!", f"{t}s")
                            time.sleep(1)
                        st.toast("Drill Finished!")

                with t2:
                    st.markdown("#### ⏱️ Rest Timer")
                    try:
                        rest_secs = int(''.join(filter(str.isdigit, str(drill['rest']))))
                    except:
                        rest_secs = 60
                    if st.button(f"Start Rest", key=f"tmr_{i}"):
                        ph = st.empty()
                        for t in range(rest_secs, -1, -1):
                            ph.metric("Resting...", f"{t}s")
                            time.sleep(1)
                        st.balloons()

                st.markdown("---")
                if "http" in str(drill['video']):
                    st.video(drill['video'])
                st.file_uploader("Upload Form Clip", type=['mp4', 'mov'], key=f"up_{i}")

    # --- 7. POST WORKOUT SUMMARY ---
    st.divider()
    if st.button("🏁 FINISH WORKOUT & VIEW SUMMARY", use_container_width=True):
        st.balloons()
        st.header("📝 Post-Workout Summary")
        
        summary_data = []
        total_completed = 0
        for i, drill in enumerate(st.session_state.current_session):
            completed = st.session_state.set_counts.get(i, 0)
            total_completed += completed
            summary_data.append({
                "Exercise": drill['ex'],
                "Sets Target": drill['sets'],
                "Sets Done": completed,
                "Status": "✅ Complete" if completed >= drill['sets'] else "⚠️ Partial"
            })
        
        # Summary Visuals
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Sets", total_completed)
        m2.metric("Intensity", effort)
        m3.metric("Date", datetime.now().strftime("%m/%d/%Y"))
        
        st.table(pd.DataFrame(summary_data))
        
        st.download_button(
            label="Download Workout Report",
            data=pd.DataFrame(summary_data).to_csv(index=False),
            file_name=f"workout_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    st.info("👋 Set your filters in the sidebar and click 'Generate Workout' to begin.")
