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
        "Facility (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"],
        default=["Gym", "Floor"]
    )
    num_drills = st.slider("Target Drills", 5, 20, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING (Black Button Text) ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_color = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Force Button Text to Black */
    button, .stButton > button {{
        color: black !important;
        font-weight: 700 !important;
        background-color: white !important;
        border: 2px solid {accent_color} !important;
    }}

    div[data-testid="stExpander"] details summary {{
        background-color: {accent_color} !important;
        color: white !important;
        border-radius: 8px;
    }}
    .metric-box {{
        background: {primary_bg};
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #334155;
        margin-bottom: 5px;
    }}
    .col-label {{ font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; font-weight: bold; }}
    .col-value {{ font-size: 0.9rem; color: #F8FAFC; }}
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

def get_csv_urls(sport):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {"Basketball": "basketball.csv", "Softball": "softball.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    return f"{base}{mapping.get(sport, 'general.csv')}"

def load_and_build_workout(sport, multiplier, env_selections, limit, intensity):
    url = get_csv_urls(sport)
    try:
        df = pd.read_csv(url).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
    except: return [], []

    # Filter by Env
    clean_envs = [s.strip().lower() for s in env_selections]
    mask = df.apply(lambda x: str(x.get('Env.', x.get('Location', ''))).lower() in clean_envs or "all" in str(x.get('Env.', '')).lower(), axis=1)
    pool_df = df[mask]

    # Filter Elite Drills
    if intensity != "Elite":
        pool_df = pool_df[~pool_df['Exercise Name'].str.contains('advanced', case=False, na=False)]

    # 1. Warmups (6-10 Drills)
    warmup_df = pool_df[pool_df['type'].str.contains('warmup', case=False, na=False)]
    warmups = warmup_df.sample(min(len(warmup_df), random.randint(6, 10))).to_dict('records') if not warmup_df.empty else []

    # 2. Main Workout
    main_df = pool_df[~pool_df['type'].str.contains('warmup', case=False, na=False)]
    
    if sport == "Basketball" and not main_df.empty:
        # Algorithm: Random type or 90/10 split
        chosen_type = random.choice(main_df['type'].unique())
        type_df = main_df[main_df['type'] == chosen_type]
        
        if len(type_df) >= limit:
            selected_df = type_df.sample(limit)
        else:
            core = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
            core_df = main_df[main_df['type'].str.lower().isin(core)]
            other_df = main_df[~main_df['type'].str.lower().isin(core)]
            n_core = int(limit * 0.9)
            selected_df = pd.concat([core_df.sample(min(len(core_df), n_core)), 
                                     other_df.sample(min(len(other_df), limit-n_core))])
    else:
        selected_df = main_df.sample(min(len(main_df), limit)) if not main_df.empty else pd.DataFrame()

    def process_row(row):
        # Scale values but keep original row data
        processed = row.copy()
        processed['Sets'] = int(round(int(float(row.get('Sets', 3))) * multiplier))
        processed['Reps/Dist'] = scale_text(row.get('Reps/Dist', row.get('Reps', '10')), multiplier)
        return processed

    return [process_row(r) for r in warmups], [process_row(r.to_dict()) for _, r in selected_df.iterrows()]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    w, m = load_and_build_workout(sport_choice, mult, location_filter, num_drills, effort)
    if m:
        st.session_state.warmup_drills = w
        st.session_state.current_session = m
        st.session_state.set_counts = {i: 0 for i in range(len(m))}
        st.session_state.workout_finished = False
    else:
        st.error("No drills found. Adjust filters.")

# --- 6. INTERFACE ---
st.title("🏆 PRO-ATHLETE PERFORMANCE")

if st.session_state.current_session and not st.session_state.workout_finished:
    # Warmup Section
    if st.session_state.warmup_drills:
        with st.expander("🔥 WARMUP (Not in count)", expanded=False):
            for wd in st.session_state.warmup_drills:
                st.write(f"• **{wd.get('Exercise Name', 'Drill')}**: {wd.get('Reps/Dist', '10')}")

    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{i+1}. {drill.get('Exercise Name', 'Drill')}", expanded=(i==0)):
            # DYNAMIC COLUMN DISPLAY: Show EVERYTHING in the file
            cols = st.columns(4)
            for idx, (key, val) in enumerate(drill.items()):
                with cols[idx % 4]:
                    st.markdown(f"<div class='metric-box'><p class='col-label'>{key}</p><p class='col-value'>{val}</p></div>", unsafe_allow_html=True)

            st.divider()
            
            # Tools Section
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill.get('Sets', 3)})", key=f"log_{i}"):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                
                if "Proper Form" in drill and drill["Proper Form"] != "N/A":
                    st.warning(f"**✨ Proper Form:** {drill['Proper Form']}")

            with c2:
                st.write("### ⏱️ Stopwatch")
                sw_col1, sw_col2 = st.columns(2)
                if sw_col1.button("Start", key=f"start_{i}"):
                    st.session_state.stopwatch_runs[i] = time.time()
                
                if sw_col2.button("Stop", key=f"stop_{i}"):
                    if i in st.session_state.stopwatch_runs:
                        elapsed = time.time() - st.session_state.stopwatch_runs[i]
                        st.info(f"Time: {elapsed:.2f}s")
                        del st.session_state.stopwatch_runs[i]
                
                if i in st.session_state.stopwatch_runs:
                    st.write("⏱️ Timer Running...")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Great Session!")
    if st.button("New Workout"):
        st.session_state.current_session = None
        st.rerun()
