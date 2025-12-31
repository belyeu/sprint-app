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
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "General"],
        default=["Gym", "Weight Room"]
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
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    div[data-testid="stExpander"] { 
        border: 1px solid #2563EB44 !important;
        border-radius: 12px !important;
        border-top: none !important;
    }
    .field-label { font-size: 0.7rem; color: #64748b; font-weight: bold; text-transform: uppercase; margin-bottom: -5px;}
    .field-value { font-size: 0.95rem; font-weight: 600; margin-bottom: 10px; color: #1E293B; }
    [data-theme="dark"] .field-value { color: #F8FAFC; }
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

def scale_text(val_str, multiplier):
    val_str = str(val_str)
    if val_str == "N/A": return "N/A"
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {"Basketball": f"{base}basketball.csv", "Softball": f"{base}softball.csv", "Track": f"{base}track.csv", "General": f"{base}general.csv"}
    load_list = [urls[sport]]
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
        if any(name == s.get('ex') for s in selected): continue

        # REPS LOGIC: Default to 10 if N/A
        raw_reps = item.get('Reps/Dist', 'N/A')
        processed_reps = "10" if raw_reps == "N/A" else scale_text(raw_reps, multiplier)

        # TIMER LOGIC: HS Standard priority
        hs_goal_val = item.get('HS Goals', 'N/A')
        timer_seconds = extract_seconds(hs_goal_val) if any(char.isdigit() for char in hs_goal_val) else extract_seconds(item.get('Time Goal', '60'))

        # REST LOGIC: CNS-based recommended rest
        cns_load = str(item.get('CNS', 'Low')).capitalize()
        rest_recommendation = {"Low": "45s", "Moderate": "90s", "High": "3m", "Elite": "5m"}.get(cns_load, "60s")
        final_rest = item.get('Rest Time', rest_recommendation)

        drill = {
            "rank": item.get('Rank', 'N/A'),
            "ex": name,
            "level": item.get('Level', 'N/A'),
            "env": item.get('Env.', 'General'),
            "muscle": item.get('Primary Muscle', 'N/A'),
            "cns": cns_load,
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": processed_reps,
            "time_goal": timer_seconds,
            "rest": final_rest,
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "hs": scale_text(hs_goal_val, multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See demo.'),
            "form": item.get('Proper Form', 'Maintain core stability.'),
            "demo": str(item.get('Demo', '')).strip()
        }
        selected.append(drill)
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_comprehensive_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.workout_finished = False

# --- 6. MAIN UI ---
st.title("🏆 PRO-ATHLETE PERFORMANCE")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"#{drill['rank']} {drill['ex']} | {drill['stars']}", expanded=(i==0)):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<p class='field-label'>Level</p><p class='field-value'>{drill['level']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='field-label'>CNS Load</p><p class='field-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<p class='field-label'>Environment</p><p class='field-value'>{drill['env']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='field-label'>Primary Muscle</p><p class='field-value'>{drill['muscle']}</p>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<p class='field-label'>Sets</p><p class='field-value'>{drill['sets']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='field-label'>Reps/Dist</p><p class='field-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<p class='field-label'>Timer Goal</p><p class='field-value'>{drill['time_goal']}s</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='field-label'>Rec. Rest</p><p class='field-value'>{drill['rest']}</p>", unsafe_allow_html=True)

            st.divider()
            
            f1, f2, f3 = st.columns(3)
            with f1: st.markdown(f"<p class='field-label'>Primary Focus</p><p class='field-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            with f2: st.info(f"**HS Standard:** {drill['hs']}")
            with f3: st.success(f"**College Goal:** {drill['coll']}")

            st.write(f"**Description:** {drill['desc']}")
            st.write(f"**Proper Form:** {drill['form']}")
            
            st.divider()
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo'] and "http" in drill['demo']: st.video(drill['demo'])
            with col_b:
                st.markdown(f"#### ⏱️ {drill['time_goal']}s Standard Timer")
                if st.button("Start Timer", key=f"t_btn_{i}"):
                    ph = st.empty()
                    for t in range(int(drill['time_goal']), -1, -1):
                        ph.metric("Seconds Remaining", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                st.file_uploader("Upload Form Clip", type=['mp4', 'mov'], key=f"f_{i}")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Session Complete!")
    st.table(pd.DataFrame(st.session_state.current_session)[['rank', 'ex', 'sets', 'reps', 'time_goal']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
