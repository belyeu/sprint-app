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
    with st.expander("Edit Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["weight"] = st.number_input("Weight", value=st.session_state.user_profile["weight"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect(
        "Facility Location", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"],
        default=["Gym", "Floor"]
    )
    num_drills = st.slider("Target Drills", 5, 20, 13)
    
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING (Blue Text & Fixed Visibility) ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_blue = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Force Button Text to Blue and Background to White/Light Gray for Visibility */
    div.stButton > button {{
        color: {accent_blue} !important;
        background-color: #FFFFFF !important;
        border: 2px solid {accent_blue} !important;
        font-weight: 800 !important;
    }}
    
    /* Alert/Bubble Boxes */
    .desc-bubble {{ background-color: #334155; padding: 15px; border-radius: 10px; border-left: 5px solid {accent_blue}; margin-bottom: 10px; }}
    .form-bubble {{ background-color: #064e3b; padding: 15px; border-radius: 10px; border-left: 5px solid #10b981; margin-bottom: 10px; }}
    
    div[data-testid="stExpander"] details summary {{
        background-color: {accent_blue} !important;
        color: white !important;
        border-radius: 8px;
    }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_blue}; font-weight: 700; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
def scale_text(val_str, multiplier):
    nums = re.findall(r'\d+', str(val_str))
    new_str = str(val_str)
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

    # Warmups
    warmup_pool = [r for r in pool if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10))) if warmup_pool else []

    # Main Selection
    main_pool = [r for r in pool if "warmup" not in str(r.get('type', '')).lower()]
    
    # Select Random Type
    available_types = list(set([str(r.get('type', '')) for r in main_pool if r.get('type') != 'N/A']))
    chosen_type = random.choice(available_types) if available_types else None
    type_matches = [r for r in main_pool if str(r.get('type', '')) == chosen_type]
    
    # 90/10 Logic if needed
    if len(type_matches) < limit:
        core = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
        core_pool = [r for r in main_pool if str(r.get('type', '')).lower() in core]
        other_pool = [r for r in main_pool if str(r.get('type', '')).lower() not in core]
        n_core = int(limit * 0.9)
        selected_candidates = random.sample(core_pool, min(len(core_pool), n_core)) + random.sample(other_pool, min(len(other_pool), limit))
    else:
        selected_candidates = random.sample(type_matches, limit)

    # Pairing Logic (L/R and Inside/Outside)
    final_workout = []
    seen_names = set()
    
    for drill in selected_candidates:
        name = str(drill.get('Exercise Name', drill.get('Exercise', '')))
        if name in seen_names: continue
        
        final_workout.append(drill)
        seen_names.add(name)
        
        # Define pairing patterns
        pairs = [("left", "right"), ("(L)", "(R)"), ("inside", "outside")]
        for p1, p2 in pairs:
            pair_name = None
            if p1 in name.lower(): pair_name = name.lower().replace(p1, p2)
            elif p2 in name.lower(): pair_name = name.lower().replace(p2, p1)
            
            if pair_name:
                match = next((r for r in main_pool if str(r.get('Exercise Name', r.get('Exercise', ''))).lower() == pair_name), None)
                if match and str(match.get('Exercise Name', '')) not in seen_names:
                    final_workout.append(match)
                    seen_names.add(str(match.get('Exercise Name', '')))

    # Process and Scale
    def process(d):
        d['Sets_S'] = int(round(int(float(d.get('Sets', 3))) * multiplier))
        d['Reps_S'] = scale_text(d.get('Reps/Dist', d.get('Reps', '10')), multiplier)
        return d

    return [process(w) for w in warmups], [process(m) for m in final_workout[:limit]]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT"):
    w_up, m_w = load_and_build_workout(sport_choice, mult, location_filter, num_drills, effort)
    st.session_state.warmup_drills = w_up
    st.session_state.current_session = m_w
    st.session_state.set_counts = {i: 0 for i in range(len(m_w))}
    st.session_state.workout_finished = False

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    # Always suggest warmups
    with st.container():
        st.markdown("### 🔥 Suggested Warmup List")
        if st.session_state.warmup_drills:
            cols = st.columns(2)
            for idx, wd in enumerate(st.session_state.warmup_drills):
                cols[idx % 2].markdown(f"✅ **{wd.get('Exercise Name', 'Drill')}**: {wd.get('Reps_S', '10')}")
        else:
            st.write("Perform 5-10 mins of dynamic stretching.")

    st.divider()

    for i, drill in enumerate(st.session_state.current_session):
        # Exclude removed columns
        exclude = ['Exercise Name', 'Exercise', 'Demo', 'Demo_URL', 'Rank', 'Description', 'Proper Form', 'Sets_S', 'Reps_S']
        
        with st.expander(f"**{drill.get('Exercise Name', 'Drill')}**", expanded=(i==0)):
            # Header Metrics
            m_cols = st.columns(4)
            visible_keys = [k for k in drill.keys() if k not in exclude]
            for idx, k in enumerate(visible_keys[:8]): # Show first 8 metadata keys
                with m_cols[idx % 4]:
                    st.markdown(f"<p class='metric-label'>{k}</p><p class='metric-value'>{drill[k]}</p>", unsafe_allow_html=True)
            
            # Reps/Sets Focus
            st.markdown(f"**Target:** <span style='color:{accent_blue}; font-size:1.2rem;'>{drill['Sets_S']} Sets x {drill['Reps_S']}</span>", unsafe_allow_html=True)
            
            # Bubbles for Info
            st.markdown(f"<div class='desc-bubble'><b>📝 Description:</b><br>{drill.get('Description', 'No description available.')}</div>", unsafe_allow_html=True)
            if drill.get('Proper Form') != "N/A":
                st.markdown(f"<div class='form-bubble'><b>✨ Proper Form:</b><br>{drill.get('Proper Form', '')}</div>", unsafe_allow_html=True)
            
            # Actions
            act1, act2 = st.columns(2)
            with act1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['Sets_S']})", key=f"l_{i}"):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
            
            with act2:
                # Stopwatch with visible counter
                sw_s, sw_x = st.columns(2)
                if sw_s.button("Start Stopwatch", key=f"ss_{i}"):
                    st.session_state.stopwatch_runs[i] = time.time()
                if sw_x.button("Stop Stopwatch", key=f"sx_{i}"):
                    if i in st.session_state.stopwatch_runs: del st.session_state.stopwatch_runs[i]
                
                if i in st.session_state.stopwatch_runs:
                    elapsed = time.time() - st.session_state.stopwatch_runs[i]
                    st.markdown(f"<h3 style='text-align:center; color:{accent_blue};'>{round(elapsed, 1)}s</h3>", unsafe_allow_html=True)

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Session Complete!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
