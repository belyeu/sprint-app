import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'warmup_drills' not in st.session_state:
    st.session_state.warmup_drills = None
if 'stopwatch_runs' not in st.session_state:
    st.session_state.stopwatch_runs = {}

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "age": 17,
        "weight": 180,
        "goal_weight": 190,
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }

if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. SIDEBAR & FILTERS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile & Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        col1, col2 = st.columns(2)
        st.session_state.user_profile["age"] = col1.number_input("Age", min_value=10, max_value=50, value=st.session_state.user_profile["age"])
        st.session_state.user_profile["weight"] = col2.number_input("Weight (lbs)", value=st.session_state.user_profile["weight"])
        st.session_state.user_profile["goal_weight"] = st.number_input("Goal Weight (lbs)", value=st.session_state.user_profile["goal_weight"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"],
        default=["Gym", "Floor"]
    )
    num_drills = st.slider("Target Drills", 5, 20, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
sidebar_text = "#F8FAFC" if dark_mode else "#1E293B"
border_color = "#3B82F6" if dark_mode else "#CBD5E1"
accent_color = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    section[data-testid="stSidebar"] {{ background-color: {primary_bg}; }}
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {{ color: {sidebar_text} !important; }}

    /* Mandatory Black Button Text */
    div.stButton > button {{
        color: black !important;
        font-weight: 700 !important;
        background-color: #F8FAFC !important;
    }}

    /* Proper Form Bubble */
    .form-bubble {{
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 5px solid {accent_color};
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0px;
    }}

    div[data-testid="stExpander"] details summary {{
        background-color: {accent_color} !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    div[data-testid="stExpander"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 12px !important; 
    }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin-bottom: 0px; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; margin-top: 0px; }}
    h1, h2, h3, p, span {{ color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
def scale_text(val_str, multiplier):
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def load_and_build_workout(sport, multiplier, env_selections, limit, intensity):
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    sport_map = {"Basketball": "basketball.csv", "Softball": "softball.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    
    try:
        df = pd.read_csv(f"{base_url}{sport_map.get(sport)}").fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        all_rows = df.to_dict('records')
    except: return [], []

    clean_envs = [s.strip().lower() for s in env_selections]
    pool = [r for r in all_rows if str(r.get('Env.', r.get('Location', ''))).lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    if intensity != "Elite":
        pool = [r for r in pool if "advance" not in str(r.get('type', '')).lower()]

    # 1. Warmups (6-10 Drills) - Excluded from target count
    warmup_pool = [r for r in pool if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10))) if warmup_pool else []

    # 2. Main Selection Logic
    main_pool = [r for r in pool if "warmup" not in str(r.get('type', '')).lower()]
    selected_main = []

    if main_pool:
        # Type-based selection
        available_types = list(set([str(r.get('type', '')) for r in main_pool if r.get('type') != 'N/A']))
        chosen_type = random.choice(available_types) if available_types else None
        type_matches = [r for r in main_pool if str(r.get('type', '')) == chosen_type]
        
        # 90/10 Logic if chosen type is small
        if len(type_matches) < limit:
            core = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
            core_pool = [r for r in main_pool if str(r.get('type', '')).lower() in core]
            other_pool = [r for r in main_pool if str(r.get('type', '')).lower() not in core]
            n_core = int(limit * 0.9)
            type_matches = random.sample(core_pool, min(len(core_pool), n_core)) + \
                           random.sample(other_pool, min(len(other_pool), max(0, limit - n_core)))

        # Pairing Logic (L/R, Left/Right, Inside/Outside)
        final_list = []
        seen_names = set()
        
        for drill in type_matches:
            if len(final_list) >= limit: break
            name = str(drill.get('Exercise Name', drill.get('Exercise', '')))
            if name in seen_names: continue
            
            final_list.append(drill)
            seen_names.add(name)
            
            # Define pairs
            pairs = [("left", "right"), ("(L)", "(R)"), ("inside", "outside")]
            for p1, p2 in pairs:
                search_name = None
                if p1 in name.lower(): search_name = name.lower().replace(p1, p2)
                elif p2 in name.lower(): search_name = name.lower().replace(p2, p1)
                
                if search_name:
                    pair_drill = next((r for r in main_pool if str(r.get('Exercise Name', r.get('Exercise', ''))).lower() == search_name), None)
                    if pair_drill and str(pair_drill.get('Exercise Name')) not in seen_names:
                        final_list.append(pair_drill)
                        seen_names.add(str(pair_drill.get('Exercise Name')))
        
        selected_main = final_list[:limit]

    # Scaling
    for d in selected_main + warmups:
        d['Sets_S'] = int(round(int(float(d.get('Sets', 3))) * multiplier))
        d['Reps_S'] = scale_text(d.get('Reps/Dist', d.get('Reps', '10')), multiplier)
    
    return warmups, selected_main

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    w_up, m_w = load_and_build_workout(sport_choice, mult, location_filter, num_drills, effort)
    st.session_state.warmup_drills = w_up
    st.session_state.current_session = m_w
    st.session_state.set_counts = {i: 0 for i in range(len(m_w))}
    st.session_state.workout_finished = False

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    # 🏋️ Warmup Suggestion List
    if st.session_state.warmup_drills:
        st.subheader("🔥 Recommended Warmup")
        warmup_text = ""
        for wd in st.session_state.warmup_drills:
            warmup_text += f"• **{wd.get('Exercise Name', 'Drill')}** ({wd.get('Reps_S', '10')})  \n"
        st.info(warmup_text)

    # 📝 Exercise Display
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill.get('Exercise Name', 'Drill')}**", expanded=(i==0)):
            
            # Proper Form Bubble (Separate and First)
            if drill.get('Proper Form') and drill.get('Proper Form') != "N/A":
                st.markdown(f"""<div class='form-bubble'><b>✨ Proper Form:</b><br>{drill['Proper Form']}</div>""", unsafe_allow_html=True)
            
            # Information Grid (Removing Description from text wall)
            cols = st.columns(4)
            keys_to_show = [k for k in drill.keys() if k not in ['Sets_S', 'Reps_S', 'Description', 'Proper Form', 'Sets', 'Reps/Dist']]
            for idx, k in enumerate(keys_to_show):
                with cols[idx % 4]:
                    st.markdown(f"<p class='metric-label'>{k}</p><p class='metric-value'>{drill[k]}</p>", unsafe_allow_html=True)
            
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['Sets_S']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                
                if "http" in str(drill.get('Demo', '')):
                    st.markdown(f"[🎥 Video Demo]({drill['Demo']})")

            with c2:
                st.markdown("#### ⏱️ Tools")
                if st.button("Start Timer", key=f"t_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(60, -1, -1):
                        ph.markdown(f"<h3 style='text-align:center;'>{t}s</h3>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.success("Finished!")

                sw1, sw2 = st.columns(2)
                if sw1.button("Start Stopwatch", key=f"sw_s_{i}", use_container_width=True):
                    st.session_state.stopwatch_runs[i] = time.time()
                if sw2.button("Stop Stopwatch", key=f"sw_x_{i}", use_container_width=True):
                    if i in st.session_state.stopwatch_runs:
                        del st.session_state.stopwatch_runs[i]
                
                if i in st.session_state.stopwatch_runs:
                    elapsed = time.time() - st.session_state.stopwatch_runs[i]
                    st.markdown(f"<h3 style='text-align:center; color:#3B82F6;'>{round(elapsed, 1)}s</h3>", unsafe_allow_html=True)

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Session Complete!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
