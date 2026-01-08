import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# Initialize Session State
state_keys = {
    'current_session': None,
    'archives': [],
    'view_archive_index': None,
    'set_counts': {},
    'stopwatch_start': {},
    'stopwatch_results': {},
    'workout_finished': False,
    'user_profile': {
        "name": "Elite Athlete", 
        "age": 17, 
        "weight": 180, 
        "goal_weight": 190, 
        "hs_goal": "Elite Performance", 
        "college_goal": "D1 Scholarship"
    }
}

for key, val in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = val

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- SOUND EFFECT HELPERS ---
def play_sound(url):
    st.markdown(f"""<audio autoplay><source src="{url}" type="audio/mp3"></audio>""", unsafe_allow_html=True)

# --- 2. SIDEBAR & FILTERS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile & Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        col1, col2 = st.columns(2)
        st.session_state.user_profile["age"] = col1.number_input("Age", value=st.session_state.user_profile["age"])
        st.session_state.user_profile["weight"] = col2.number_input("Weight (lbs)", value=st.session_state.user_profile["weight"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Field", "Cages"])
    num_drills = st.slider("Target Drills", 1, 50, 13)
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_color = "#3B82F6"
bubble_bg = "#334155" if dark_mode else "#E2E8F0"
form_bubble_bg = "#422006" if dark_mode else "#FEF3C7"
form_text_color = "#FCD34D" if dark_mode else "#92400E"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] span {{
        color: #000000 !important; font-weight: 700 !important;
    }}
    div[data-testid="stExpander"] details summary span p, div[data-testid="stExpander"] details summary {{
        color: #FFFFFF !important; font-weight: 800 !important;
    }}
    .stButton > button {{ color: #000000 !important; font-weight: 600 !important; }}
    .desc-bubble {{ background-color: {bubble_bg}; padding: 15px; border-radius: 12px; border-left: 5px solid {accent_color}; margin-bottom: 10px; }}
    .form-bubble {{ background-color: {form_bubble_bg}; color: {form_text_color} !important; padding: 15px; border-radius: 12px; border-left: 5px solid #F59E0B; margin-bottom: 10px; }}
    div[data-testid="stExpander"] details summary {{ background-color: {accent_color} !important; border-radius: 8px; }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {accent_color} !important; }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin: 0; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; margin: 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC & GROUPING ENGINE ---
def scale_text(val_str, multiplier):
    nums = re.findall(r'\d+', str(val_str))
    new_str = str(val_str)
    for n in nums:
        new_str = new_str.replace(n, str(int(round(int(n) * multiplier))), 1)
    return new_str

def extract_clean_url(text):
    if not isinstance(text, str): return None
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else None

def sequence_drills(drill_list):
    """Sorts drills so paired types (L/R, In/Out, Front/Back) stay together."""
    def get_group_key(name):
        name = name.lower()
        base = re.sub(r'\b(left|right|l/|r/|inside|outside|front|back|l |r )\b', '', name).strip()
        return base
    return sorted(drill_list, key=lambda x: get_group_key(x['ex']))

def load_and_build_workout(sport, multiplier, env_selections, limit):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {"Basketball": "basketball.csv", "Softball": "softball.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    
    load_list = [f"{base}{mapping.get(sport, 'general.csv')}"]
    if "Weight Room" in env_selections:
        load_list += [f"{base}barbell.csv", f"{base}general-dumbell.csv", f"{base}general-kettlebell.csv"]
    
    all_rows = []
    for url in load_list:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
    
    if not all_rows: return []

    clean_envs = [s.strip().lower() for s in env_selections]
    filtered_pool = []
    for r in all_rows:
        row_loc = str(r.get('Environment', r.get('Env.', r.get('Location', 'All')))).strip().lower()
        if any(env in row_loc for env in clean_envs) or row_loc in ["all", "n/a", "general", ""]:
            filtered_pool.append(r)
    
    if not filtered_pool: filtered_pool = all_rows
    
    random.shuffle(filtered_pool)

    # BASKETBALL LOGIC: Type Lock
    if sport == "Basketball" and filtered_pool:
        first_drill_cat = filtered_pool[0].get('Category', 'Skill')
        # Only keep drills from the same category as the first random drill
        filtered_pool = [r for r in filtered_pool if r.get('Category') == first_drill_cat]

    selected_raw = []
    seen = set()
    for item in filtered_pool:
        if len(selected_raw) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen or name == "Unknown": continue
        seen.add(name)
        
        raw_sets = str(item.get('Sets', 3))
        found_digits = re.findall(r'\d+', raw_sets)
        base_sets = int(found_digits[0]) if found_digits else 3
        
        selected_raw.append({
            "ex": name, 
            "category": item.get('Category', 'Skill'),
            "sets": int(round(base_sets * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps/Dist.', '10')), multiplier),
            "env": item.get('Environment', item.get('Env.', 'General')),
            "focus": item.get('Primary Focus', 'N/A'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "hs": item.get('High School Goals (Time/Dist.)', item.get('HS Goals', 'N/A')),
            "coll": item.get('College Goals (Time/Dist.)', item.get('College Goals', 'N/A')),
            "desc": item.get('Detailed Description', item.get('Description', 'No description provided.')),
            "form": item.get('Proper Form', 'Focus on technique.'),
            "equip": item.get('Equipment Needed', 'N/A'),
            "demo": extract_clean_url(str(item.get('Demo', item.get('Demo_URL', ''))))
        })
    
    return sequence_drills(selected_raw)

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.stopwatch_start = {}
        st.session_state.stopwatch_results = {}
        st.session_state.workout_finished = False
        st.rerun()

# --- 6. MAIN INTERFACE ---
if st.session_state.current_session:
    current_cat = st.session_state.current_session[0]['category']
    st.markdown(f"<h3 style='text-align: center; color: #3B82F6;'>Focus Session: {current_cat}</h3>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE: {drill['ex'].upper()} | {drill['stars']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🛠️ Equip</p><p class='metric-value'>{drill['equip']}</p>", unsafe_allow_html=True)

            st.markdown(f"<div class='desc-bubble'><strong>📝 Description:</strong> {drill['desc']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='form-bubble'><strong>✨ Proper Form:</strong> {drill['form']}</div>", unsafe_allow_html=True)

            col_actions, col_watch = st.columns([1, 1])
            with col_actions:
                if st.button(f"✅ Log Set ({st.session_state.set_counts.get(i,0)}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    play_sound("https://www.myinstants.com/media/sounds/ding-sound-effect_1.mp3")
                    st.rerun()

            with col_watch:
                if i not in st.session_state.stopwatch_start:
                    if st.button("⏱️ Start Clock", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    elapsed_now = time.time() - st.session_state.stopwatch_start[i]
                    if st.button(f"🛑 Stop ({elapsed_now:.1f}s)", key=f"stop_{i}", use_container_width=True):
                        st.session_state.stopwatch_results[i] = f"{elapsed_now:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()

            if drill['demo']:
                st.markdown("---")
                v_col1, v_col2, v_col3 = st.columns([1, 2, 1])
                with v_col2:
                    try: st.video(drill['demo'])
                    except: st.error("Video unavailable.")

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        play_sound("https://www.myinstants.com/media/sounds/referee-whistle.mp3")
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.header("📊 Session Summary")
    if st.button("Start New Session", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Please use the sidebar to generate a new workout session.")
