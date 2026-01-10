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

state_keys = {
    'current_session': None,
    'archives': [],
    'view_archive_index': None,
    'set_counts': {},
    'stopwatch_start': {},
    'stopwatch_results': {},
    'workout_finished': False,
    'user_profile': {"name": "Elite Athlete", "age": 17, "weight": 180}
}

for key, val in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = val

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DATA LOADING HELPER (PRE-SCAN) ---
@st.cache_data
def get_csv_data(sport):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    mapping = {
        "Basketball": "basketball.csv", 
        "Softball": "softball-hitting.csv", 
        "Track": "track.csv", 
        "Pilates": "pilates.csv", 
        "General": "general.csv"
    }
    url = f"{base}{mapping.get(sport, 'general.csv')}"
    try:
        df = pd.read_csv(url).fillna("N/A")
        # Clean whitespace from headers
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def find_column_ignore_case(df, target_name):
    """Finds the actual column name in the DF that matches target_name (case-insensitive)."""
    for col in df.columns:
        if col.lower() == target_name.lower():
            return col
    return None

# --- 3. SIDEBAR & DYNAMIC FILTERS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("📍 SESSION FILTERS")
    
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_choice = st.selectbox("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"])

    # Define the mapping of Sport -> Desired Column Name
    col_map = {
        "General": "Primary Muscle",
        "Track": "type",
        "Basketball": "type",
        "Softball": "Category"
    }
    requested_col = col_map.get(sport_choice, "Category")

    # PRE-SCAN CSV FOR FILTER OPTIONS
    df_preview = get_csv_data(sport_choice)
    filter_options = ["All"]
    actual_col_name = None

    if not df_preview.empty:
        # Find the actual column in the CSV (e.g., if 'type' is 'Type' or 'type')
        actual_col_name = find_column_ignore_case(df_preview, requested_col)
        
        if actual_col_name:
            raw_options = df_preview[actual_col_name].unique().tolist()
            # Filter out N/A and clean up strings
            clean_opts = sorted([str(opt) for opt in raw_options if str(opt) != "N/A"])
            filter_options += clean_opts
        else:
            st.sidebar.warning(f"Column '{requested_col}' not found in file.")

    type_filter = st.selectbox(f"Filter by {requested_col}", filter_options)
    
    num_drills = st.slider("Target Drills", 1, 50, 13)
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 4. DYNAMIC THEMING ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {"#0F172A" if dark_mode else "#FFFFFF"}; color: {"#F8FAFC" if dark_mode else "#1E293B"}; }}
    
    /* SIDEBAR TEXT TO BLACK */
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] span {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] {{ background-color: #F1F5F9 !important; }}

    /* FACILITY NAME BACKGROUND BLUE, TEXT WHITE */
    div[data-testid="stExpander"] details summary {{
        background-color: #1E40AF !important;
        color: #FFFFFF !important;
        border-radius: 8px; padding: 10px;
    }}
    
    /* EXERCISE NAMES TO WHITE */
    div[data-testid="stExpander"] details summary span p {{
        color: #FFFFFF !important; font-weight: 800 !important;
    }}

    /* BLACK BUTTON TEXT */
    .stButton > button {{ color: #000000 !important; font-weight: 600 !important; }}
    
    .desc-bubble {{ background-color: #334155; padding: 15px; border-radius: 12px; border-left: 5px solid #3B82F6; margin-bottom: 10px; }}
    .form-bubble {{ background-color: #422006; color: #FCD34D !important; padding: 15px; border-radius: 12px; border-left: 5px solid #F59E0B; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. WORKOUT BUILDER ---
def scale_text(val_str, multiplier):
    nums = re.findall(r'\d+', str(val_str))
    new_str = str(val_str)
    for n in nums:
        new_str = new_str.replace(n, str(int(round(int(n) * multiplier))), 1)
    return new_str

def load_and_build_workout(sport, multiplier, location, limit, type_filter, target_col_name):
    df = get_csv_data(sport)
    if df.empty: return []

    all_rows = df.to_dict('records')
    actual_col = find_column_ignore_case(df, target_col_name)

    filtered_pool = []
    for r in all_rows:
        # Standardize location check
        row_loc = str(r.get('Environment', r.get('Env.', r.get('Location', 'All')))).strip().lower()
        # Standardize type check using actual column name found
        row_type = str(r.get(actual_col, 'General')).strip().lower() if actual_col else "general"
        
        loc_match = (location.lower() in row_loc) or row_loc in ["all", "general", "n/a", ""]
        type_match = (type_filter.lower() == "all") or (type_filter.lower() == row_type)
        
        if loc_match and type_match:
            filtered_pool.append(r)
    
    if not filtered_pool: filtered_pool = all_rows
    
    random.shuffle(filtered_pool)
    selected = []
    seen = set()
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen or name == "Unknown": continue
        seen.add(name)
        
        raw_sets = str(item.get('Sets', 3))
        found_digits = re.findall(r'\d+', raw_sets)
        base_sets = int(found_digits[0]) if found_digits else 3
        
        selected.append({
            "ex": name, 
            "sets": int(round(base_sets * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps/Dist.', '10')), multiplier),
            "focus": item.get('Primary Focus', 'N/A'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "hs": item.get('High School Goals (Time/Dist.)', item.get('HS Goals', 'N/A')),
            "coll": item.get('College Goals (Time/Dist.)', item.get('College Goals', 'N/A')),
            "desc": item.get('Detailed Description', item.get('Description', 'N/A')),
            "form": item.get('Proper Form', 'Focus on technique.'),
            "equip": item.get('Equipment Needed', 'N/A'),
            "demo": item.get('Demo', item.get('Demo_URL', None))
        })
    return selected

# --- 6. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_choice, num_drills, type_filter, requested_col)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.stopwatch_start = {}
        st.session_state.stopwatch_results = {}
        st.session_state.workout_finished = False
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"EXERCISE: {drill['ex'].upper()} | {drill['stars']}", expanded=(i==0)):
            # Metric Columns
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
                    if st.button("Start Timer", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    if st.button("🛑 Stop & Save", key=f"stop_{i}", use_container_width=True):
                        elapsed = time.time() - st.session_state.stopwatch_start[i]
                        st.session_state.stopwatch_results[i] = f"{elapsed:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()
                    st.error(f"Timer Running: {time.time() - st.session_state.stopwatch_start[i]:.1f}s")
    
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        final = [{"Exercise": d['ex'], "Sets": st.session_state.set_counts.get(idx, 0), "Time": st.session_state.stopwatch_results.get(idx, "N/A")} for idx, d in enumerate(st.session_state.current_session)]
        st.session_state.archives.append({"date": get_now_est().strftime('%Y-%m-%d %H:%M'), "data": final})
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.header("📊 Session Summary")
    df_summary = pd.DataFrame(st.session_state.archives[-1]['data'])
    st.table(df_summary)
    
    csv = df_summary.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download CSV", data=csv, file_name=f"workout_{get_now_est().strftime('%Y%m%d')}.csv", mime='text/csv')
    
    if st.button("Start New Session", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Please use the sidebar to generate a new workout session.")
