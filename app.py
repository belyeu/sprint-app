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
    section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: {sidebar_text} !important;
    }}
    
    /* Force Button Text to Black in Dark Mode */
    .stButton > button {{
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

def get_csv_urls(sport):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {
        "Basketball": f"{base}basketball.csv",
        "Softball": f"{base}softball.csv",
        "Track": f"{base}track.csv",
        "Pilates": f"{base}pilates.csv", 
        "General": f"{base}general.csv"
    }
    return urls.get(sport, urls["General"])

def load_and_build_workout(sport, multiplier, env_selections, limit):
    url = get_csv_urls(sport)
    try:
        df = pd.read_csv(url).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        all_rows = df.to_dict('records')
    except:
        return [], []

    clean_envs = [s.strip().lower() for s in env_selections]
    pool = [r for r in all_rows if str(r.get('Env.', r.get('Location', 'General'))).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]

    # 1. Warmups (6-10 Drills) - Not in main count
    warmup_pool = [r for r in pool if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 10))) if warmup_pool else []

    # 2. Main Workout
    main_pool = [r for r in pool if str(r.get('type', '')).lower() not in ['warmup', 'w_room']]
    selected_rows = []

    if sport == "Basketball" and main_pool:
        available_types = list(set([str(r.get('type', '')) for r in main_pool if str(r.get('type', '')) != 'N/A']))
        if available_types:
            random_type = random.choice(available_types)
            type_matches = [r for r in main_pool if str(r.get('type', '')) == random_type]
            
            if len(type_matches) >= limit:
                selected_rows = random.sample(type_matches, limit)
            else:
                # 90/10 Logic
                core_cats = ['shooting', 'movement', 'footwork', 'ball-handle', 'finish', 'defense']
                core_pool = [r for r in main_pool if str(r.get('type', '')).lower() in core_cats]
                other_pool = [r for r in main_pool if str(r.get('type', '')).lower() not in core_cats]
                
                n_core = min(len(core_pool), int(limit * 0.9))
                n_other = limit - n_core
                selected_rows = random.sample(core_pool, n_core) + random.sample(other_pool, min(len(other_pool), n_other))
        else:
            selected_rows = random.sample(main_pool, min(len(main_pool), limit))
    elif main_pool:
        selected_rows = random.sample(main_pool, min(len(main_pool), limit))

    def process_item(item):
        sets_val = 3
        try: sets_val = int(float(item.get('Sets', 3)))
        except: pass
        return {
            **item, # Keep all existing columns
            "ex": item.get('Exercise Name', item.get('Exercise', 'Unknown')),
            "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps', '10')), multiplier),
            "demo": extract_clean_url(str(item.get('Demo', item.get('Demo_URL', ''))))
        }

    return [process_item(i) for i in warmups], [process_item(i) for i in selected_rows]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    w_up, main_w = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if main_w:
        st.session_state.warmup_drills = w_up
        st.session_state.current_session = main_w
        st.session_state.set_counts = {i: 0 for i in range(len(main_w))}
        st.session_state.workout_finished = False
        st.session_state.stopwatch_runs = {}
    else:
        st.error("No drills found. Try adjusting your filters.")

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)
p = st.session_state.user_profile
st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h3>Athlete: {p['name']} | Weight: {p['weight']}lbs</h3></div>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    if st.session_state.warmup_drills:
        with st.expander("🔥 SUGGESTED WARMUP (6-10 Drills)", expanded=False):
            for wd in st.session_state.warmup_drills:
                st.write(f"• **{wd['ex']}**: {wd['reps']}")

    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** | {drill.get('Stars', '⭐⭐⭐')}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill.get('Env.', 'General')}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>📂 Type</p><p class='metric-value'>{drill.get('type', 'Skill')}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill.get('CNS', 'Low')}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill.get('Primary Focus', 'Performance')}</p>", unsafe_allow_html=True)
            
            st.divider()
            m5, m6, m7, m8 = st.columns(4)
            m5.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m6.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m7.markdown(f"<p class='metric-label'>🕒 Time</p><p class='metric-value'>{drill.get('Time', 'N/A')}</p>", unsafe_allow_html=True)
            m8.markdown(f"<p class='metric-label'>⚠️ Pre-Req</p><p class='metric-value'>{drill.get('Pre-Req', 'N/A')}</p>", unsafe_allow_html=True)

            st.write(f"**📝 Description:** {drill.get('Description', 'N/A')}")
            # RESTORE PROPER FORM
            pf = drill.get('Proper Form', drill.get('proper_form', 'N/A'))
            if pf != "N/A":
                st.warning(f"**✨ Proper Form:** {pf}")
            
            st.divider()
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}", use_container_width=True):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo']:
                    st.video(drill['demo'])

            with col_b:
                st.markdown("#### ⏱️ Timer & Stopwatch")
                t_val = st.number_input("Seconds", 5, 600, 60, key=f"ti_{i}")
                if st.button("Start Timer", key=f"tb_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(int(t_val), -1, -1):
                        ph.markdown(f"<h3 style='text-align:center; color:{accent_color};'>{t}s</h3>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.markdown("<h3 style='text-align:center;'>✅ Time's Up!</h3>", unsafe_allow_html=True)
                
                sw_col1, sw_col2 = st.columns(2)
                if sw_col1.button("Start Stopwatch", key=f"sw_start_{i}", use_container_width=True):
                    st.session_state.stopwatch_runs[i] = time.time()
                
                if sw_col2.button("Stop Stopwatch", key=f"sw_stop_{i}", use_container_width=True):
                    if i in st.session_state.stopwatch_runs:
                        elapsed = time.time() - st.session_state.stopwatch_runs[i]
                        st.session_state[f"sw_res_{i}"] = round(elapsed, 2)
                        # FIXED: Proper if statement instead of ternary del
                        if i in st.session_state.stopwatch_runs:
                            del st.session_state.stopwatch_runs[i]
                
                if f"sw_res_{i}" in st.session_state:
                    st.success(f"Last Time: {st.session_state[f'sw_res_{i}']}s")

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success(f"Workout Complete!")
    summary_data = [{"Exercise": d['ex'], "Sets": d['sets'], "Reps": d['reps']} for d in st.session_state.current_session]
    st.table(pd.DataFrame(summary_data))
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Use the sidebar to set your profile and generate a session.")
