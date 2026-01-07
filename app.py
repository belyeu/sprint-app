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

# Updated Profile Dictionary with new fields
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

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

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

    st.markdown(f"**Date:** {get_now_est().strftime('%Y-%m-%d')}")

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
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{ color: {sidebar_text} !important; }}

    /* CHANGE: Action Buttons to Black Text */
    div.stButton > button {{
        color: black !important;
        font-weight: 700 !important;
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
        border-top: none !important;
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

def get_csv_url(sport):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {
        "Basketball": "basketball.csv",
        "Softball": "softball.csv",
        "Track": "track.csv",
        "General": "general.csv",
        "Pilates": "pilates.csv"
    }
    return f"{base}{mapping.get(sport, 'general.csv')}"

def load_and_build_workout(sport, multiplier, env_selections, limit, intensity):
    url = get_csv_url(sport)
    try:
        df = pd.read_csv(url).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        all_rows = df.to_dict('records')
    except: return [], []

    clean_envs = [s.strip().lower() for s in env_selections]
    pool = [r for r in all_rows if str(r.get('Env.', r.get('Location', ''))).lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    # Intensity Filter
    if intensity != "Elite":
        pool = [r for r in pool if "advance" not in str(r.get('type', '')).lower()]

    # Warmups (6-10 Drills)
    warmup_pool = [r for r in pool if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10))) if warmup_pool else []

    # Main Workout Algorithm
    main_pool = [r for r in pool if "warmup" not in str(r.get('type', '')).lower()]
    selected_main = []

    if main_pool:
        # Pick a random type first
        available_types = list(set([str(r.get('type', 'Unknown')) for r in main_pool if r.get('type') != 'N/A']))
        chosen_type = random.choice(available_types) if available_types else "Unknown"
        
        type_matches = [r for r in main_pool if str(r.get('type', '')) == chosen_type]
        
        if len(type_matches) >= limit:
            selected_main = random.sample(type_matches, limit)
        else:
            # 90/10 Fallback
            core_cats = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
            core_pool = [r for r in main_pool if str(r.get('type', '')).lower() in core_cats]
            other_pool = [r for r in main_pool if str(r.get('type', '')).lower() not in core_cats]
            
            n_core = int(limit * 0.9)
            selected_main = random.sample(core_pool, min(len(core_pool), n_core)) + \
                           random.sample(other_pool, min(len(other_pool), limit - n_core))

    # Pairing Logic
    final_drills = []
    seen_names = set()
    for drill in selected_main:
        name = str(drill.get('Exercise Name', drill.get('Exercise', '')))
        if name in seen_names: continue
        final_drills.append(drill)
        seen_names.add(name)
        
        if "left" in name.lower() or "(L)" in name:
            pair_name = name.replace("left", "right").replace("Left", "Right").replace("(L)", "(R)")
            pair = next((r for r in main_pool if str(r.get('Exercise Name', r.get('Exercise', ''))) == pair_name), None)
            if pair and pair.get('Exercise Name', pair.get('Exercise', '')) not in seen_names:
                final_drills.append(pair)
                seen_names.add(pair.get('Exercise Name', pair.get('Exercise', '')))

    # Scaling Logic
    for d in final_drills + warmups:
        try: raw_sets = int(float(d.get('Sets', 3)))
        except: raw_sets = 3
        d['sets_scaled'] = int(round(raw_sets * multiplier))
        d['reps_scaled'] = scale_text(d.get('Reps/Dist', d.get('Reps', '10')), multiplier)
    
    return warmups, final_drills[:limit]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    w_up, m_w = load_and_build_workout(sport_choice, mult, location_filter, num_drills, effort)
    st.session_state.warmup_drills = w_up
    st.session_state.current_session = m_w
    st.session_state.set_counts = {i: 0 for i in range(len(m_w))}
    st.session_state.workout_finished = False
    st.session_state.stopwatch_runs = {}

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    # Warmups
    if st.session_state.warmup_drills:
        with st.expander("🔥 SUGGESTED WARMUP (6-10 Drills)", expanded=False):
            for wd in st.session_state.warmup_drills:
                st.write(f"• **{wd.get('Exercise Name', 'Drill')}**: {wd.get('reps_scaled', '10')}")

    # Main Exercises
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill.get('Exercise Name', drill.get('Exercise', 'Drill'))}**", expanded=(i==0)):
            
            # Display all columns from CSV
            cols = st.columns(4)
            all_keys = [k for k in drill.keys() if k not in ['sets_scaled', 'reps_scaled']]
            for idx, key in enumerate(all_keys):
                with cols[idx % 4]:
                    st.markdown(f"<p class='metric-label'>{key}</p><p class='metric-value'>{drill[key]}</p>", unsafe_allow_html=True)
            
            st.divider()
            
            # Proper Form Restoration
            if drill.get('Proper Form') and drill.get('Proper Form') != "N/A":
                st.warning(f"**✨ Proper Form:** {drill['Proper Form']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                target = drill.get('sets_scaled', 3)
                if st.button(f"✅ Log Set ({curr}/{target})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                
                demo_link = str(drill.get('Demo', drill.get('Demo_URL', '')))
                if "http" in demo_link:
                    st.markdown(f"[🎥 View Demo Video]({demo_link})")

            with col_b:
                st.markdown("#### ⏱️ Timer & Stopwatch")
                if st.button("Start Timer", key=f"t_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(60, -1, -1):
                        ph.markdown(f"<h3 style='text-align:center;'>{t}s</h3>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.success("Finished!")

                # Stopwatch Counter
                s1, s2 = st.columns(2)
                if s1.button("Start Stopwatch", key=f"sw_start_{i}", use_container_width=True):
                    st.session_state.stopwatch_runs[i] = time.time()
                if s2.button("Stop Stopwatch", key=f"sw_stop_{i}", use_container_width=True):
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
    st.success("Workout Complete!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👈 Use the sidebar to generate a session.")
