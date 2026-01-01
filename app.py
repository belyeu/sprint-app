import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

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
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. SIDEBAR & FILTERS ---
with st.sidebar:
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
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
st.markdown("""
    <style>
    div[data-testid="stExpander"] details summary {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .field-label { font-size: 0.7rem; color: #64748b; font-weight: bold; text-transform: uppercase; margin-bottom: -5px;}
    .field-value { font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; color: #2563EB; }
    .timer-alert {
        padding: 15px;
        background-color: #EF4444;
        color: white;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
def extract_seconds(text):
    text = str(text).lower()
    m_ss = re.search(r'(\d+):(\d+)', text)
    if m_ss: return int(m_ss.group(1)) * 60 + int(m_ss.group(2))
    ss = re.search(r'(\d+)\s*(s|sec)', text)
    if ss: return int(ss.group(1))
    fallback = re.search(r'\d+', text)
    return int(fallback.group()) if fallback else 60

def scale_text(val_str, multiplier, is_reps=False):
    val_str = str(val_str)
    if is_reps and (val_str.upper() == "N/A" or val_str.strip() == ""): return "10"
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {"Basketball": f"{base}basketball.csv", "Softball": f"{base}softball.csv", 
            "Track": f"{base}track.csv", "Pilates": f"{base}pilates.csv", "General": f"{base}general.csv"}
    load_list = [urls.get(sport, urls["General"])]
    load_list += [f"{base}general-loop-band.csv", f"{base}general-mini-bands.csv"]
    if "Weight Room" in selected_envs:
        load_list += [f"{base}barbell.csv", f"{base}general-cable-crossover.csv", f"{base}general-dumbell.csv", f"{base}general-kettlebell.csv", f"{base}general-medball.csv"]
    return load_list

def load_comprehensive_workout(sport, multiplier, env_selections, limit):
    urls = get_csv_urls(sport, env_selections)
    all_rows = []
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
    
    clean_envs = [s.strip().lower() for s in env_selections]
    filtered_pool = [r for r in all_rows if str(r.get('Env.', 'General')).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    if not filtered_pool: return []
    random.shuffle(filtered_pool)
    
    selected = []
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        
        hs_goal_text = item.get('HS Goals', 'N/A')
        time_val = item.get('Time Goal', item.get('Time', 'N/A'))
        timer_seconds = extract_seconds(hs_goal_text if time_val == "N/A" else time_val)

        drill = {
            "rank": item.get('Rank', 'N/A'),
            "ex": name,
            "level": item.get('Level', 'N/A'),
            "env": item.get('Env.', 'General'),
            "muscle": item.get('Primary Muscle', 'N/A'),
            "cns": item.get('CNS', 'Low'),
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier, is_reps=True),
            "time_goal": f"{timer_seconds}s",
            "rest": item.get('Rest Time', '60s'),
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "hs": scale_text(hs_goal_text, multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'N/A'),
            "form": item.get('Proper Form', 'N/A'),
            "demo": str(item.get('Demo', '')).strip()
        }
        selected.append(drill)
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    st.session_state.current_session = load_comprehensive_workout(sport_choice, mult, location_filter, num_drills)
    st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
    st.session_state.workout_finished = False

# --- 6. MAIN UI ---
st.title("🏆 PRO-ATHLETE PERFORMANCE")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"#{drill['rank']} {drill['ex']} | {drill['stars']}", expanded=(i==0)):
            # DISPLAYING ALL 17 REQUESTED FIELDS
            # Group 1: Identity & Environment
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            r1c1.markdown(f"<p class='field-label'>Rank</p><p class='field-value'>{drill['rank']}</p>", unsafe_allow_html=True)
            r1c2.markdown(f"<p class='field-label'>Level</p><p class='field-value'>{drill['level']}</p>", unsafe_allow_html=True)
            r1c3.markdown(f"<p class='field-label'>Env</p><p class='field-value'>{drill['env']}</p>", unsafe_allow_html=True)
            r1c4.markdown(f"<p class='field-label'>Primary Muscle</p><p class='field-value'>{drill['muscle']}</p>", unsafe_allow_html=True)

            # Group 2: Load & Volume
            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            r2c1.markdown(f"<p class='field-label'>CNS</p><p class='field-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            r2c2.markdown(f"<p class='field-label'>Sets</p><p class='field-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            r2c3.markdown(f"<p class='field-label'>Reps/Dist</p><p class='field-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            r2c4.markdown(f"<p class='field-label'>Time Goal</p><p class='field-value'>{drill['time_goal']}</p>", unsafe_allow_html=True)

            # Group 3: Recovery & Focus
            r3c1, r3c2, r3c3, r3c4 = st.columns(4)
            r3c1.markdown(f"<p class='field-label'>Rest Time</p><p class='field-value'>{drill['rest']}</p>", unsafe_allow_html=True)
            r3c2.markdown(f"<p class='field-label'>Primary Focus</p><p class='field-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            r3c3.markdown(f"<p class='field-label'>Stars</p><p class='field-value'>{drill['stars']}</p>", unsafe_allow_html=True)
            r3c4.markdown(f"<p class='field-label'>Pre-Req</p><p class='field-value'>{drill['pre_req']}</p>", unsafe_allow_html=True)

            # Group 4: Goals
            r4c1, r4c2 = st.columns(2)
            r4c1.info(f"**HS Goals:** {drill['hs']}")
            r4c2.success(f"**College Goals:** {drill['coll']}")

            # Group 5: Detailed Content
            st.markdown(f"**Description:** {drill['desc']}")
            st.markdown(f"**Proper Form:** {drill['form']}")
            
            st.divider()
            
            # Interactive Area
            act1, act2 = st.columns([1, 1])
            with act1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo'] and "http" in drill['demo']: st.video(drill['demo'])
            
            with act2:
                st.markdown("#### ⏱️ Timer Alert System")
                rest_secs = extract_seconds(drill['rest'])
                t_val = st.number_input("Adjust Rest (s)", 1, 600, rest_secs, key=f"t_val_{i}")
                
                timer_ph = st.empty()
                if st.button("Start Timer", key=f"t_btn_{i}", use_container_width=True):
                    for t in range(int(t_val), -1, -1):
                        timer_ph.metric("Rest Remaining", f"{t}s")
                        time.sleep(1)
                    timer_ph.markdown('<div class="timer-alert">🚨 TIME EXPIRED! START NEXT SET! 🚨</div>', unsafe_allow_html=True)
                    st.toast("Rest Over!", icon="🔔")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Session Logged Successfully!")
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.rerun()
