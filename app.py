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
if 'archives' not in st.session_state:
    st.session_state.archives = [] 
if 'view_archive_index' not in st.session_state:
    st.session_state.view_archive_index = None

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
    st.header("📂 WORKOUT HISTORY")
    if st.session_state.archives:
        archive_names = [f"{a['date']} - {a['sport']}" for a in st.session_state.archives]
        selected_arch = st.selectbox("Pull up past session:", ["Current / New"] + archive_names)
        if selected_arch != "Current / New":
            idx = archive_names.index(selected_arch)
            st.session_state.view_archive_index = idx
        else:
            st.session_state.view_archive_index = None
    else:
        st.caption("No archived workouts yet.")

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
    location_filter = st.multiselect("Facility Location (Env.)", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Floor"])
    
    # NEW: Toggle to select all drills
    all_drills_toggle = st.checkbox("Select All Available Drills", value=True)
    if not all_drills_toggle:
        num_drills = st.slider("Target Drills", 5, 30, 13)
    else:
        num_drills = 999  # Effectively unlimited
    
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
    div[data-testid="stExpander"] details summary {{ background-color: {accent_color} !important; color: white !important; border-radius: 8px; padding: 0.6rem 1rem; font-weight: 600; margin-bottom: 10px; }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 12px !important; border-top: none !important; }}
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

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {"Basketball": f"{base}basketball.csv", "Softball": f"{base}softball.csv", "Track": f"{base}track.csv", "Pilates": f"{base}pilates.csv", "General": f"{base}general.csv"}
    load_list = [urls.get(sport, urls["General"])]
    load_list += [f"{base}general-loop-band.csv", f"{base}general-mini-bands.csv"]
    if "Weight Room" in selected_envs:
        load_list += [f"{base}barbell.csv", f"{base}general-cable-crossover.csv", f"{base}general-dumbell.csv", f"{base}general-kettlebell.csv", f"{base}general-medball.csv"]
    return load_list

def load_and_build_workout(sport, multiplier, env_selections, limit):
    urls = get_csv_urls(sport, env_selections)
    all_rows = []
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
    if not all_rows: return []
    
    clean_envs = [s.strip().lower() for s in env_selections]
    filtered_pool = []
    for r in all_rows:
        row_loc = str(r.get('Env.', r.get('Location', 'General'))).strip().lower()
        if row_loc in clean_envs or "all" in row_loc:
            filtered_pool.append(r)
    if not filtered_pool: return []

    # FIX: Sort by Category to keep types together (Defense, P&R, Shoot, etc.)
    filtered_pool.sort(key=lambda x: str(x.get('Category', 'General')))

    selected = []
    seen_names = set()
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen_names: continue
        seen_names.add(name)
        try: sets_val = int(float(item.get('Sets', 3)))
        except: sets_val = 3
        
        drill = {
            "ex": name, "env": item.get('Env.', item.get('Location', 'General')), "category": item.get('Category', 'Skill'),
            "cns": item.get('CNS', 'Low'), "focus": item.get('Primary Focus', 'Performance'), "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'), "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps', '10')), multiplier), "time": item.get('Time', 'N/A'),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier), "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See demo for form.'), "proper_form": item.get('Proper Form', 'Maintain core stability and breathing.'), "demo": extract_clean_url(str(item.get('Demo', item.get('Demo_URL', ''))))
        }
        selected.append(drill)
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.workout_finished = False
        st.session_state.view_archive_index = None
    else:
        st.error("No drills found. Try adjusting your filters.")

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

# Athlete Header Info
p = st.session_state.user_profile
st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h3>Athlete: {p['name']} | Age: {p['age']} | Weight: {p['weight']}lbs (Goal: {p['goal_weight']}lbs)</h3></div>", unsafe_allow_html=True)

# Archive Logic
if st.session_state.view_archive_index is not None:
    arch = st.session_state.archives[st.session_state.view_archive_index]
    st.info(f"📁 Viewing Archived Session: {arch['date']} ({arch['sport']})")
    st.table(pd.DataFrame(arch['data']))
    if st.button("Close Archive"):
        st.session_state.view_archive_index = None
        st.rerun()

# Current Session Logic
elif st.session_state.current_session and not st.session_state.workout_finished:
    current_cat = ""
    for i, drill in enumerate(st.session_state.current_session):
        # UI: Show Category Header to highlight the grouping
        if drill['category'] != current_cat:
            st.markdown(f"### 🎯 {drill['category']}")
            current_cat = drill['category']

        with st.expander(f"**{i+1}. {drill['ex']}** |  {drill['stars']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>📂 Category</p><p class='metric-value'>{drill['category']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            
            st.divider()
            
            m5, m6, m7, m8 = st.columns(4)
            m5.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m6.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m7.markdown(f"<p class='metric-label'>🕒 Time</p><p class='metric-value'>{drill['time']}</p>", unsafe_allow_html=True)
            m8.markdown(f"<p class='metric-label'>⚠️ Pre-Req</p><p class='metric-value'>{drill['pre_req']}</p>", unsafe_allow_html=True)

            st.write(f"**📝 Description:** {drill['desc']}")
            st.divider()
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}", use_container_width=True):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo']:
                    try: st.video(drill['demo'])
                    except: st.markdown(f"[🎥 Watch Video]({drill['demo']})")

            with col_b:
                tab_timer, tab_stopwatch = st.tabs(["🕒 Countdown", "⏱️ Stopwatch"])
                with tab_timer:
                    t_val = st.number_input("Seconds", 5, 600, 60, key=f"timer_input_{i}")
                    if st.button("Start Timer", key=f"timer_btn_{i}", use_container_width=True):
                        ph = st.empty()
                        for t in range(int(t_val), -1, -1):
                            ph.markdown(f"<h3 style='text-align:center; color:{accent_color};'>{t}s</h3>", unsafe_allow_html=True)
                            time.sleep(1)
                        ph.markdown("<h3 style='text-align:center;'>✅ Time's Up!</h3>", unsafe_allow_html=True)
                with tab_stopwatch:
                    if st.button("Start Stopwatch", key=f"sw_btn_{i}", use_container_width=True):
                        ph_sw = st.empty()
                        start_time = time.time()
                        while True:
                            elapsed = time.time() - start_time
                            ph_sw.markdown(f"<h2 style='text-align:center; color:#FF4B4B;'>{elapsed:.1f}s</h2>", unsafe_allow_html=True)
                            time.sleep(0.1)

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        summary_data = [{"Exercise": d['ex'], "Sets": d['sets'], "Reps": d['reps']} for d in st.session_state.current_session]
        st.session_state.archives.append({"date": get_now_est().strftime('%Y-%m-%d %H:%M'), "sport": sport_choice, "data": summary_data})
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Workout Complete! Saved to History.")
    summary_data = [{"Exercise": d['ex'], "Sets": d['sets'], "Reps": d['reps']} for d in st.session_state.current_session]
    st.table(pd.DataFrame(summary_data))
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Use the sidebar to set your profile, pull up history, or generate a session.")
