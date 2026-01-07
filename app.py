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
    st.session_state.warmup_drills = []
if 'stopwatch_running' not in st.session_state:
    st.session_state.stopwatch_running = {}

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

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
sidebar_text = "#F8FAFC" if dark_mode else "#1E293B"
border_color = "#3B82F6" if dark_mode else "#CBD5E1"
accent_color = "#3B82F6"

# CSS for Button Text Color and layout
st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Target Specific Buttons to have BLACK text in Dark Mode */
    div.stButton > button {{
        color: black !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] {{ background-color: {primary_bg}; }}
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{ color: {sidebar_text} !important; }}

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
    
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC & SCALING ---
def scale_text(val_str, multiplier):
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def extract_clean_url(text):
    if not isinstance(text, str): return ""
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else ""

def load_and_build_workout(sport, multiplier, env_selections, limit):
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv"
    try:
        df = pd.read_csv(base_url).fillna("N/A")
    except:
        st.error("Could not load basketball.csv")
        return [], []

    # Filter for Location/Env
    clean_envs = [s.strip().lower() for s in env_selections]
    df['env_match'] = df['Env.'].apply(lambda x: str(x).strip().lower() in clean_envs or "all" in str(x).lower())
    df = df[df['env_match']]

    # 1. Generate Warmups (6-10 drills, type='warmup')
    warmup_pool = df[df['type'].str.lower() == 'warmup'].to_dict('records')
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10)))

    # 2. Main Workout Logic
    # Identify unique types except warmup and w_room
    excluded = ['warmup', 'w_room']
    available_types = [t for t in df['type'].unique() if t.lower() not in excluded]
    
    if not available_types: return [], warmups

    # Pick a random type for the primary focus
    primary_type = random.choice(available_types)
    type_pool = df[df['type'] == primary_type].to_dict('records')
    
    selected_drills = []
    
    # Try to fill with primary type
    if len(type_pool) >= limit:
        selected_drills = random.sample(type_pool, limit)
    else:
        # 90% Primary (or all available), 10% Others
        selected_drills = type_pool
        remainder_count = limit - len(selected_drills)
        
        # Pool for the "Other" 10%
        other_pool = df[~df['type'].isin([primary_type] + excluded)].to_dict('records')
        if other_pool:
            selected_drills += random.sample(other_pool, min(len(other_pool), remainder_count))

    # Format drills for the UI
    final_workout = []
    for item in selected_drills:
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        sets_val = 3
        try: sets_val = int(float(item.get('Sets', 3)))
        except: pass

        final_workout.append({
            "ex": name,
            "env": item.get('Env.', 'General'),
            "category": item.get('type', 'Skill'),
            "cns": item.get('CNS', 'Low'),
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', '10'), multiplier),
            "time": item.get('Time', 'N/A'),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See demo.'),
            "proper_form": item.get('Proper Form', 'Keep back straight, engage core.'),
            "demo": extract_clean_url(str(item.get('Demo', '')))
        })
    
    return final_workout, warmups

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    work, warm = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    st.session_state.current_session = work
    st.session_state.warmup_drills = warm
    st.session_state.set_counts = {i: 0 for i in range(len(work))}
    st.session_state.workout_finished = False
    st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.warmup_drills and not st.session_state.workout_finished:
    with st.expander("🔥 PRE-WORKOUT WARMUP (Recommended)", expanded=False):
        for w in st.session_state.warmup_drills:
            st.markdown(f"**• {w.get('Exercise Name', 'Warmup Drill')}** - {w.get('Reps/Dist', '10 reps')}")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** | {drill['category']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)
            
            st.info(f"**✨ Proper Form:** {drill['proper_form']}")
            
            col_left, col_right = st.columns(2)
            with col_left:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                
                if drill['demo']:
                    st.video(drill['demo'])

            with col_right:
                st.markdown("#### ⏱️ Timers")
                t_col1, t_col2 = st.columns(2)
                
                if t_col1.button("Start Timer", key=f"t_start_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(60, -1, -1):
                        ph.markdown(f"**Time Left: {t}s**")
                        time.sleep(1)
                    ph.success("Done!")

                # --- STOPWATCH FEATURE ---
                if f"sw_{i}" not in st.session_state: st.session_state[f"sw_{i}"] = 0
                
                sw_btn = t_col2.button("Start Stopwatch" if not st.session_state.stopwatch_running.get(i) else "Stop", key=f"sw_btn_{i}", use_container_width=True)
                
                if sw_btn:
                    st.session_state.stopwatch_running[i] = not st.session_state.stopwatch_running.get(i, False)
                    if st.session_state.stopwatch_running[i]:
                        st.session_state[f"sw_start_{i}"] = time.time()
                
                if st.session_state.stopwatch_running.get(i):
                    elapsed = time.time() - st.session_state[f"sw_start_{i}"]
                    st.markdown(f"**Elapsed:** {elapsed:.1f}s")
                    time.sleep(0.1)
                    st.rerun()

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Session Complete!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
