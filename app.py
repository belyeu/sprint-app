import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

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

# --- 2. SIDEBAR & DYNAMIC FILTERS ---
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
    location_choice = st.selectbox("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"])
    
    # Dynamic Column Mapping
    if sport_choice == "General": type_col = "primary muscle"
    elif sport_choice == "Softball": type_col = "category"
    elif sport_choice in ["Track", "Basketball"]: type_col = "type"
    else: type_col = "type"

    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {"Basketball": "basketball.csv", "Softball": "softball-hitting.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    
    try:
        df_temp = pd.read_csv(f"{base_url}{mapping.get(sport_choice)}").fillna("N/A")
        df_temp.columns = [c.strip().lower() for c in df_temp.columns]
        opts = ["All"] + sorted([str(x).title() for x in df_temp[type_col].unique() if str(x) != "N/A"])
    except:
        opts = ["All"]

    selected_type = st.selectbox(f"Filter by {type_col.title()}", opts)
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
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p {{
        color: #000000 !important; font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] {{ background-color: #F1F5F9 !important; }}
    div[data-testid="stExpander"] details summary {{
        background-color: #1E40AF !important; color: #FFFFFF !important; border-radius: 8px; font-weight: 800 !important;
    }}
    div[data-testid="stExpander"] details summary span p {{ color: #FFFFFF !important; }}
    [data-testid="stTable"] td, [data-testid="stTable"] th {{ color: {text_color} !important; }}
    .stButton > button {{ color: #000000 !important; font-weight: 600 !important; }}
    .desc-bubble {{ background-color: {bubble_bg}; padding: 15px; border-radius: 12px; border-left: 5px solid {accent_color}; margin-bottom: 10px; }}
    .form-bubble {{ background-color: {form_bubble_bg}; color: {form_text_color} !important; padding: 15px; border-radius: 12px; border-left: 5px solid #F59E0B; margin-bottom: 10px; }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin: 0; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; margin: 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA PROCESSING LOGIC ---
def scale_text(val_str, multiplier):
    nums = re.findall(r'\d+', str(val_str))
    new_str = str(val_str)
    for n in nums:
        new_str = new_str.replace(n, str(int(round(int(n) * multiplier))), 1)
    return new_str

def extract_clean_url(text):
    """Aggressive URL extraction to catch links inside complex strings."""
    if not isinstance(text, str) or text.strip() == "" or text == "N/A": 
        return None
    # Look for standard http/https or youtube/vimeo signatures
    match = re.search(r'(https?://[^\s\'"<>]+)', text)
    return match.group(1) if match else None

def load_and_build_workout(sport, multiplier, location, limit, t_filter, t_col):
    try:
        df = pd.read_csv(f"{base_url}{mapping.get(sport)}").fillna("N/A")
        df.columns = [c.strip().lower() for c in df.columns]
        all_rows = df.to_dict('records')
    except: return []
    
    if location == "Weight Room":
        for extra in ["barbell.csv", "general-dumbell.csv", "general-kettlebell.csv"]:
            try:
                ex_df = pd.read_csv(f"{base_url}{extra}").fillna("N/A")
                ex_df.columns = [c.strip().lower() for c in ex_df.columns]
                all_rows.extend(ex_df.to_dict('records'))
            except: continue
    
    filtered_pool = []
    for r in all_rows:
        row_loc = str(r.get('environment', r.get('env.', r.get('location', 'all')))).strip().lower()
        row_type = str(r.get(t_col, 'skill')).strip().lower()
        loc_match = (location.lower() in row_loc) or row_loc in ["all", "n/a", "general", ""]
        type_match = (t_filter.lower() == "all") or (t_filter.lower() == row_type)
        if loc_match and type_match:
            filtered_pool.append(r)
    
    random.shuffle(filtered_pool)
    selected = []
    seen = set()
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('exercise name', item.get('exercise', 'Unknown'))
        if name in seen or name == "Unknown": continue
        seen.add(name)
        
        # --- FIXED VIDEO DISCOVERY FOR GENERAL CSV ---
        video_url = None
        # Check every possible column name for a video link
        for key in ['demo', 'video', 'url', 'demo_url', 'link', 'youtube']:
            raw_val = str(item.get(key, ''))
            video_url = extract_clean_url(raw_val)
            if video_url: break

        raw_sets = str(item.get('sets', 3))
        found_digits = re.findall(r'\d+', raw_sets)
        base_sets = int(found_digits[0]) if found_digits else 3
        
        selected.append({
            "ex": name, "sets": int(round(base_sets * multiplier)),
            "reps": scale_text(item.get('reps/dist', item.get('reps/dist.', '10')), multiplier),
            "focus": item.get('primary focus', 'N/A'),
            "stars": item.get('stars', '⭐⭐⭐'),
            "desc": item.get('detailed description', item.get('description', 'N/A')),
            "form": item.get('proper form', 'Focus on technique.'),
            "equip": item.get('equipment needed', 'N/A'),
            "demo": video_url
        })
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_choice, num_drills, selected_type, type_col)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.stopwatch_start = {}
        st.session_state.stopwatch_results = {}
        st.session_state.workout_finished = False
        st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE: {drill['ex'].upper()} | {drill['stars']}", expanded=(i==0)):
            # Demo Video Placement
            if drill['demo']:
                st.video(drill['demo'])
            else:
                st.caption("No demo video available for this exercise.")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🛠️ Equipment</p><p class='metric-value'>{drill['equip']}</p>", unsafe_allow_html=True)

            st.markdown(f"<div class='desc-bubble'><strong>📝 Description:</strong><br>{drill['desc']}</div><div class='form-bubble'><strong>✨ Proper Form:</strong><br>{drill['form']}</div>", unsafe_allow_html=True)

            col_actions, col_watch = st.columns([1, 1])
            with col_actions:
                if st.button(f"✅ Log Set ({st.session_state.set_counts.get(i,0)}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()

            with col_watch:
                if i not in st.session_state.stopwatch_start:
                    if st.button("⏱️ Start Timer", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    timer_placeholder = st.empty()
                    start_val = st.session_state.stopwatch_start[i]
                    if st.button("🛑 Stop & Save", key=f"stop_{i}", use_container_width=True):
                        final_time = time.time() - start_val
                        st.session_state.stopwatch_results[i] = f"{final_time:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()
                    elapsed = time.time() - start_val
                    timer_placeholder.error(f"LIVE TIMER: {elapsed:.1f}s")
                    time.sleep(0.1)
                    st.rerun()

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        final = [{"Exercise": d['ex'], "Sets": st.session_state.set_counts.get(idx, 0), "Time": st.session_state.stopwatch_results.get(idx, "N/A")} for idx, d in enumerate(st.session_state.current_session)]
        st.session_state.archives.append({"date": get_now_est().strftime('%Y-%m-%d %H:%M'), "data": final})
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.header("📊 Session Summary")
    st.table(pd.DataFrame(st.session_state.archives[-1]['data']))
    if st.button("Start New Session", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Please use the sidebar to generate a new workout session.")
