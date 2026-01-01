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
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    # Added Pilates to the list
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    # Added Floor to the locations
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
border_color = "#3B82F6" if dark_mode else "#CBD5E1"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    div[data-testid="stExpander"] details summary {{
        background-color: #2563EB !important;
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
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1.1rem; color: #3B82F6; font-weight: 700; }}
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

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {
        "Basketball": f"{base}basketball.csv",
        "Softball": f"{base}softball.csv",
        "Track": f"{base}track.csv",
        "Pilates": f"{base}pilates.csv", # Added pilates mapping
        "General": f"{base}general.csv"
    }
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
    filtered_pool = [
        r for r in all_rows 
        if str(r.get('Env.', 'General')).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()
    ]
    
    if not filtered_pool: return []
    random.shuffle(filtered_pool)
    
    selected = []
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if any(name == s.get('ex') for s in selected): continue

        drill = {
            "ex": name,
            "env": item.get('Env.', 'General'),
            "category": item.get('Category', 'Skill'),
            "cns": item.get('CNS', 'Low'),
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
            "time": item.get('Time', 'N/A'),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See demo for form.'),
            "proper_form": item.get('Proper Form', 'Maintain core stability and breathing.'), # Added column logic
            "demo": str(item.get('Demo', '')).strip()
        }
        selected.append(drill)

        side_match = re.search(r'\(L\)|\(R\)', name)
        if side_match:
            tag = "(R)" if side_match.group() == "(L)" else "(L)"
            partner_name = name.replace(side_match.group(), tag)
            for p in filtered_pool:
                p_name = p.get('Exercise Name', p.get('Exercise', ''))
                if p_name == partner_name:
                    p_drill = drill.copy()
                    p_drill['ex'] = partner_name
                    selected.append(p_drill)
                    break
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.workout_finished = False
    else:
        st.sidebar.error("No matching drills. Check locations.")

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)



if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**EXERCISE {i+1}: {drill['ex']}** | {drill['stars']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>📂 Category</p><p class='metric-value'>{drill['category']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            
            m5, m6, m7, m8 = st.columns(4)
            m5.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m6.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m7.markdown(f"<p class='metric-label'>🕒 Time</p><p class='metric-value'>{drill['time']}</p>", unsafe_allow_html=True)
            m8.markdown(f"<p class='metric-label'>⚠️ Pre-Req</p><p class='metric-value'>{drill['pre_req']}</p>", unsafe_allow_html=True)

            c9, c10 = st.columns(2)
            c9.info(f"**HS Goal:** {drill['hs']}")
            c10.success(f"**College Goal:** {drill['coll']}")

            st.write(f"**📝 Description:** {drill['desc']}")
            # Proper Form Column Display
            st.warning(f"**✨ Proper Form:** {drill['proper_form']}")
            st.divider()
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                if drill['demo'] and "http" in str(drill['demo']):
                    st.video(drill['demo'])
                else:
                    st.caption("No demo video available.")

            with col_b:
                st.markdown("#### ⏱️ Drill / Rest Timer")
                t_val = st.number_input("Seconds", 5, 600, 60, key=f"timer_input_{i}")
                if st.button("Start Timer", key=f"timer_btn_{i}"):
                    ph = st.empty()
                    for t in range(int(t_val), -1, -1):
                        ph.metric("Timer", f"{t}s")
                        time.sleep(1)
                    st.toast("Time up!")
                st.file_uploader("Upload Form Clip", type=['mp4', 'mov'], key=f"file_{i}")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Workout Summary Generated!")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'env', 'category', 'sets', 'reps']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👈 Use the sidebar to set your profile and generate a session.")
