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
    
    /* BLACK BUTTON TEXT FOR SPECIFIC BUTTONS */
    div.stButton > button {{
        color: black !important;
        font-weight: bold !important;
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
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; }}
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

def extract_clean_url(text):
    if not isinstance(text, str): return ""
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else ""

def get_csv_urls(sport):
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
    url = get_csv_urls(sport)
    try:
        df = pd.read_csv(url).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        all_rows = df.to_dict('records')
    except:
        return [], []

    clean_envs = [s.strip().lower() for s in env_selections]
    pool = [r for r in all_rows if str(r.get('Env.', r.get('Location', 'General'))).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]

    # Elite Filter: "advance" drills only for Elite intensity
    if intensity != "Elite":
        pool = [r for r in pool if "advance" not in str(r.get('type', '')).lower()]

    # 1. Warmups (6-10 Drills) - Excluded from main count
    warmup_pool = [r for r in pool if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10))) if warmup_pool else []

    # 2. Main Workout Selection
    main_pool = [r for r in pool if "warmup" not in str(r.get('type', '')).lower()]
    selected_raw = []

    if sport == "Basketball" and main_pool:
        types = list(set([r['type'] for r in main_pool if r['type'] != 'N/A']))
        chosen_type = random.choice(types) if types else "N/A"
        type_matches = [r for r in main_pool if r['type'] == chosen_type]
        
        if len(type_matches) >= limit:
            selected_raw = random.sample(type_matches, limit)
        else:
            # 90/10 Logic
            core_cats = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
            core_pool = [r for r in main_pool if str(r.get('type', '')).lower() in core_cats]
            other_pool = [r for r in main_pool if str(r.get('type', '')).lower() not in core_cats]
            n_core = int(limit * 0.9)
            selected_raw = random.sample(core_pool, min(len(core_pool), n_core)) + \
                           random.sample(other_pool, min(len(other_pool), limit - n_core))
    else:
        selected_raw = random.sample(main_pool, min(len(main_pool), limit)) if main_pool else []

    # 3. Left/Right Pairing Logic
    final_drills = []
    for drill in selected_raw:
        final_drills.append(drill)
        name = str(drill.get('Exercise Name', drill.get('Exercise', '')))
        if "left" in name.lower() or "(L)" in name:
            # Look for Right pair in the pool
            partner_name = name.replace("left", "right").replace("Left", "Right").replace("(L)", "(R)")
            partner = next((r for r in main_pool if str(r.get('Exercise Name', r.get('Exercise', ''))) == partner_name), None)
            if partner: final_drills.append(partner)

    def process(item):
        sets_val = 3
        try: sets_val = int(float(item.get('Sets', 3)))
        except: pass
        # Maintain all original columns while adding shortcut keys
        item.update({
            "ex": item.get('Exercise Name', item.get('Exercise', 'Unknown')),
            "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps', '10')), multiplier),
            "demo": extract_clean_url(str(item.get('Demo', item.get('Demo_URL', ''))))
        })
        return item

    return [process(i) for i in warmups], [process(i) for i in final_drills[:limit]]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    w_up, main_w = load_and_build_workout(sport_choice, mult, location_filter, num_drills, effort)
    if main_w:
        st.session_state.warmup_drills = w_up
        st.session_state.current_session = main_w
        st.session_state.set_counts = {i: 0 for i in range(len(main_w))}
        st.session_state.workout_finished = False
        st.session_state.stopwatch_runs = {}
    else:
        st.error("No drills found. Adjust filters.")

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)
p = st.session_state.user_profile
st.markdown(f"<div style='text-align:center;'><h3>Athlete: {p['name']} | Weight: {p['weight']}lbs</h3></div>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    if st.session_state.warmup_drills:
        with st.expander("🔥 SUGGESTED WARMUP (6-10 Drills)", expanded=False):
            for wd in st.session_state.warmup_drills:
                st.write(f"• **{wd['ex']}**: {wd['reps']}")

    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** | {drill.get('Stars', '⭐⭐⭐')}", expanded=(i==0)):
            # Show ALL columns dynamically
            cols = st.columns(4)
            visible_cols = [k for k in drill.keys() if k not in ['ex', 'sets', 'reps', 'demo']]
            for idx, key in enumerate(visible_cols[:8]):
                cols[idx % 4].markdown(f"<p class='metric-label'>{key}</p><p class='metric-value'>{drill[key]}</p>", unsafe_allow_html=True)
            
            st.divider()
            st.warning(f"**✨ Proper Form:** {drill.get('Proper Form', 'Maintain core stability.')}")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}", use_container_width=True):
                    if curr < drill['sets']:
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
                    ph.success("✅ Done!")
                
                sw_c1, sw_c2 = st.columns(2)
                if sw_c1.button("Start Stopwatch", key=f"sw_s_{i}", use_container_width=True):
                    st.session_state.stopwatch_runs[i] = time.time()
                
                if sw_c2.button("Stop Stopwatch", key=f"sw_x_{i}", use_container_width=True):
                    if i in st.session_state.stopwatch_runs:
                        elapsed = time.time() - st.session_state.stopwatch_runs[i]
                        st.session_state[f"sw_res_{i}"] = round(elapsed, 2)
                        del st.session_state.stopwatch_runs[i]
                
                if i in st.session_state.stopwatch_runs:
                    st.write(f"⏱️ Counter: {round(time.time() - st.session_state.stopwatch_runs[i], 1)}s")
                if f"sw_res_{i}" in st.session_state:
                    st.info(f"Last Lap: {st.session_state[f'sw_res_{i}']}s")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Session Logged!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
