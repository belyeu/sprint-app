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
    location_filter = st.multiselect("Env.", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Floor"])
    num_drills = st.slider("Target Drills", 5, 20, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING (FIXED BUTTON TEXT) ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_color = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Global Button Override: Forces Black Text on generated buttons */
    div.stButton > button {{
        color: black !important;
        font-weight: 700 !important;
        background-color: #CBD5E1 !important;
    }}
    div.stButton > button:hover {{
        background-color: #FFFFFF !important;
    }}

    div[data-testid="stExpander"] details summary {{
        background-color: {accent_color} !important;
        color: white !important;
        border-radius: 8px; padding: 0.6rem 1rem; font-weight: 600;
    }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {accent_color} !important; border-radius: 12px !important; }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; }}
    h1, h2, h3, p, span {{ color: {text_color} !important; }}
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
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    # Mapping sports to specific CSVs
    sport_map = {"Basketball": "basketball.csv", "Softball": "softball.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    target_csv = f"{base}{sport_map.get(sport, 'general.csv')}"
    
    try:
        df = pd.read_csv(target_csv).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
    except: return [], []

    # 1. Suggested Warmups (Not included in workout count)
    warmup_pool = df[df['type'].str.contains('warmup', case=False, na=False)]
    warmups = warmup_pool.sample(min(len(warmup_pool), random.randint(6, 10))).to_dict('records')

    # 2. Main Workout Logic
    main_pool = df[~df['type'].str.contains('warmup|w_room', case=False, na=False)]
    
    if sport == "Basketball":
        # Randomly select a type from the column
        all_types = main_pool['type'].unique().tolist()
        chosen_type = random.choice(all_types)
        type_filtered = main_pool[main_pool['type'] == chosen_type]
        
        if len(type_filtered) >= limit:
            selected_rows = type_filtered.sample(limit)
        else:
            # 90/10 Split
            core_cats = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
            core_pool = main_pool[main_pool['type'].str.lower().isin(core_cats)]
            other_pool = main_pool[~main_pool['type'].str.lower().isin(core_cats)]
            
            n_core = int(limit * 0.9)
            n_other = limit - n_core
            
            s1 = core_pool.sample(min(len(core_pool), n_core))
            s2 = other_pool.sample(min(len(other_pool), n_other))
            selected_rows = pd.concat([s1, s2])
    else:
        selected_rows = main_pool.sample(min(len(main_pool), limit))

    workout = []
    for _, item in selected_rows.iterrows():
        workout.append({
            "ex": item.get('Exercise Name', item.get('Exercise', 'Unknown')),
            "env": item.get('Env.', item.get('Location', 'General')),
            "category": item.get('type', 'Skill'),
            "cns": item.get('CNS', 'Low'),
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "sets": int(round(float(item.get('Sets', 3)) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', '10'), multiplier),
            "time": item.get('Time', 'N/A'),
            "hs": item.get('HS Goals', 'N/A'),
            "coll": item.get('College Goals', 'N/A'),
            "desc": item.get('Description', 'Follow form cues.'),
            "proper_form": item.get('Proper Form', 'Maintain core stability.'),
            "demo": extract_clean_url(str(item.get('Demo', '')))
        })
    return warmups, workout

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    wup, mmain = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if mmain:
        st.session_state.warmup_drills = wup
        st.session_state.current_session = mmain
        st.session_state.set_counts = {i: 0 for i in range(len(mmain))}
        st.session_state.workout_finished = False
        st.session_state.stopwatch_running = {}

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    # WARMUP SECTION
    with st.expander("🔥 SUGGESTED WARMUP (6-10 Drills)", expanded=False):
        for w in st.session_state.warmup_drills:
            st.markdown(f"**{w.get('Exercise Name', 'Warmup')}** - {w.get('Reps/Dist', '10 reps')}")

    # WORKOUT DRILLS
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** | {drill['stars']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>📂 Type</p><p class='metric-value'>{drill['category']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🔄 Reps</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            
            st.warning(f"**✨ Proper Form:** {drill['proper_form']}")
            st.write(f"**📝 Description:** {drill['desc']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                if drill['demo']: st.video(drill['demo'])

            with col_b:
                st.markdown("#### ⏱️ Timer & Stopwatch")
                t_val = st.number_input("Seconds", 5, 600, 60, key=f"ti_{i}")
                if st.button("Start Timer", key=f"tb_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(int(t_val), -1, -1):
                        ph.markdown(f"<h3 style='text-align:center;'>{t}s</h3>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.success("✅ Complete")

                # STOPWATCH LOGIC
                sw_key = f"sw_{i}"
                if sw_key not in st.session_state.stopwatch_running:
                    if st.button("Start Stopwatch", key=f"sw_start_{i}", use_container_width=True):
                        st.session_state.stopwatch_running[sw_key] = time.time()
                        st.rerun()
                else:
                    elapsed = time.time() - st.session_state.stopwatch_running[sw_key]
                    st.metric("Running Time", f"{elapsed:.1f}s")
                    if st.button("🛑 Stop Stopwatch", key=f"sw_stop_{i}", use_container_width=True):
                        del st.session_state.stopwatch_running[sw_key]
                        st.rerun()

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Session Complete!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👈 Use the sidebar to generate your session.")
