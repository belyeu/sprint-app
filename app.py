import streamlit as st
import pandas as pd
import random
import time
import re
import io
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
    'drill_pool': [], # Store unfiltered pool for secondary filtering
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
    
    # CHANGED: Multi-select to Single Dropdown for Facility
    location_choice = st.selectbox("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"])
    
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
    
    /* FORCE SIDEBAR TEXT TO BLACK REGARDLESS OF THEME */
    [data-testid="stSidebar"] {{
        background-color: #F1F5F9 !important;
    }}
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stSelectbox div div {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}

    /* FORCE EXERCISE NAMES TO WHITE */
    div[data-testid="stExpander"] details summary span p,
    div[data-testid="stExpander"] details summary {{
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }}

    /* SUMMARY PAGE: WHITE TEXT ON BLUE HEADERS */
    .summary-header {{
        background-color: {accent_color};
        color: #FFFFFF !important;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 800;
    }}
    
    .stButton > button {{
        color: #000000 !important;
        font-weight: 600 !important;
    }}
    
    .desc-bubble {{ background-color: {bubble_bg}; padding: 15px; border-radius: 12px; border-left: 5px solid {accent_color}; margin-bottom: 10px; }}
    .form-bubble {{ background-color: {form_bubble_bg}; color: {form_text_color} !important; padding: 15px; border-radius: 12px; border-left: 5px solid #F59E0B; margin-bottom: 10px; }}
    
    div[data-testid="stExpander"] details summary {{ background-color: {accent_color} !important; border-radius: 8px; }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {accent_color} !important; }}
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin: 0; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; margin: 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
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

def load_drill_pool(sport, env_selection):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {
        "Basketball": "basketball.csv", 
        "Softball": "softball-hitting.csv", 
        "Track": "track.csv", 
        "Pilates": "pilates.csv", 
        "General": "general.csv"
    }
    
    load_list = [f"{base}{mapping.get(sport, 'general.csv')}"]
    if env_selection == "Weight Room":
        load_list += [f"{base}barbell.csv", f"{base}general-dumbell.csv", f"{base}general-kettlebell.csv"]
    
    all_rows = []
    for url in load_list:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
    
    # Filter by location dropdown
    clean_env = env_selection.strip().lower()
    filtered = []
    for r in all_rows:
        row_loc = str(r.get('Environment', r.get('Env.', r.get('Location', 'All')))).strip().lower()
        if clean_env in row_loc or row_loc in ["all", "general", "n/a", ""]:
            filtered.append(r)
    
    return filtered if filtered else all_rows

# --- 5. TYPE SELECTION DROPDOWN ---
drill_pool = load_drill_pool(sport_choice, location_choice)
available_types = sorted(list(set([str(r.get('Category', 'Skill')) for r in drill_pool])))

with st.sidebar:
    st.divider()
    # DROPDOWN for Exercise Type (Category)
    type_choice = st.selectbox("Exercise Type", ["All"] + available_types)

if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    final_pool = drill_pool
    if type_choice != "All":
        final_pool = [r for r in drill_pool if str(r.get('Category')) == type_choice]
    
    random.shuffle(final_pool)
    selected = []
    seen = set()
    for item in final_pool:
        if len(selected) >= num_drills: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen or name == "Unknown": continue
        seen.add(name)
        
        raw_sets = str(item.get('Sets', 3))
        found_digits = re.findall(r'\d+', raw_sets)
        base_sets = int(found_digits[0]) if found_digits else 3
        
        selected.append({
            "ex": name, 
            "category": item.get('Category', 'Skill'),
            "sets": int(round(base_sets * mult)),
            "reps": scale_text(item.get('Reps/Dist', '10'), mult),
            "env": item.get('Environment', item.get('Env.', 'General')),
            "focus": item.get('Primary Focus', 'N/A'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "hs": item.get('High School Goals (Time/Dist.)', 'N/A'),
            "coll": item.get('College Goals (Time/Dist.)', 'N/A'),
            "desc": item.get('Detailed Description', 'No description provided.'),
            "form": item.get('Proper Form', 'Focus on technique.'),
            "equip": item.get('Equipment Needed', 'N/A'),
            "demo": extract_clean_url(str(item.get('Demo', '')))
        })
    
    if selected:
        st.session_state.current_session = selected
        st.session_state.set_counts = {i: 0 for i in range(len(selected))}
        st.session_state.stopwatch_start = {}
        st.session_state.stopwatch_results = {}
        st.session_state.workout_finished = False
        st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE: {drill['ex'].upper()} | {drill['stars']}", expanded=(i==0)):
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🎯 Primary Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🛠️ Equipment</p><p class='metric-value'>{drill['equip']}</p>", unsafe_allow_html=True)

            st.markdown(f"""<div class='desc-bubble'><strong>📝 Detailed Description:</strong><br>{drill['desc']}</div>
                            <div class='form-bubble'><strong>✨ Proper Form:</strong><br>{drill['form']}</div>""", unsafe_allow_html=True)
            
            col_actions, col_watch = st.columns([1, 1])
            with col_actions:
                if st.button(f"✅ Log Set ({st.session_state.set_counts.get(i,0)}/{drill['sets']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
            
            with col_watch:
                if i not in st.session_state.stopwatch_start:
                    if st.button("⏱️ Start Stopwatch", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    if st.button("🛑 Stop & Save", key=f"stop_{i}", use_container_width=True):
                        elapsed = time.time() - st.session_state.stopwatch_start[i]
                        st.session_state.stopwatch_results[i] = f"{elapsed:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()
                
                if i in st.session_state.stopwatch_results:
                    st.success(f"Recorded: {st.session_state.stopwatch_results[i]}")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        final = [{"Exercise": d['ex'], "Sets": st.session_state.set_counts.get(idx, 0), "Time": st.session_state.stopwatch_results.get(idx, "N/A")} for idx, d in enumerate(st.session_state.current_session)]
        st.session_state.archives.append({"date": get_now_est().strftime('%Y-%m-%d %H:%M'), "sport": sport_choice, "data": final})
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    # Blue background with white text for the summary header
    st.markdown("<div class='summary-header'>📊 WORKOUT SUMMARY COMPLETE</div>", unsafe_allow_html=True)
    
    df_summary = pd.DataFrame(st.session_state.archives[-1]['data'])
    st.table(df_summary)
    
    # DOWNLOADABLE SUMMARY
    csv = df_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Session Report (CSV)",
        data=csv,
        file_name=f"workout_summary_{get_now_est().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )
    
    if st.button("Start New Session", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Use the sidebar filters to generate your elite performance session.")
