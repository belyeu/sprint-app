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
    'stopwatch_start': {},  # Stores start timestamps for each drill
    'stopwatch_results': {}, # Stores final times
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
    location_filter = st.multiselect("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Floor"])
    
    select_all = st.checkbox("Select All Drills", value=True)
    num_drills = 999 if select_all else st.slider("Target Drills", 5, 50, 13)

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
    .stTable, [data-testid="stMarkdownContainer"] p, h1, h2, h3 {{ color: {text_color} !important; }}
    
    /* Bubble Styling */
    .desc-bubble {{
        background-color: {bubble_bg};
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid {accent_color};
        margin-bottom: 10px;
    }}
    .form-bubble {{
        background-color: {form_bubble_bg};
        color: {form_text_color} !important;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #F59E0B;
        margin-bottom: 10px;
    }}
    .form-bubble strong {{ color: {form_text_color} !important; }}
    
    div[data-testid="stExpander"] details summary {{ background-color: {accent_color} !important; color: white !important; border-radius: 8px; }}
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
    
    clean_envs = [s.strip().lower() for s in env_selections]
    filtered_pool = [r for r in all_rows if str(r.get('Env.', r.get('Location', 'General'))).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    if not filtered_pool: return []
    filtered_pool.sort(key=lambda x: str(x.get('Category', 'General')))
    
    selected = []
    seen = set()
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen: continue
        seen.add(name)
        
        # Capture ALL columns
        drill = {
            "ex": name, 
            "category": item.get('Category', 'Skill'),
            "sets": int(round(int(float(item.get('Sets', 3))) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', '10'), multiplier),
            "env": item.get('Env.', 'General'),
            "cns": item.get('CNS', 'N/A'),
            "focus": item.get('Primary Focus', 'N/A'),
            "hs": item.get('HS Goals', 'N/A'),
            "coll": item.get('College Goals', 'N/A'),
            "desc": item.get('Description', 'No description provided.'),
            "form": item.get('Proper Form', 'Focus on technique.'),
            "demo": str(item.get('Demo', item.get('Demo_URL', '')))
        }
        selected.append(drill)
    return selected

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
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** ({st.session_state.set_counts.get(i,0)}/{drill['sets']})", expanded=(i==0)):
            
            # 1. All Columns / Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)

            # Secondary Metrics
            c1, c2 = st.columns(2)
            if drill['hs'] != "N/A": c1.info(f"**HS Goal:** {drill['hs']}")
            if drill['coll'] != "N/A": c2.success(f"**College Goal:** {drill['coll']}")
            
            # 2. Description & Proper Form in Bubbles
            st.markdown(f"""
                <div class='desc-wrapper'>
                    <div class='desc-bubble'>
                        <strong>📝 Description:</strong><br>{drill['desc']}
                    </div>
                </div>
                <div class='form-wrapper'>
                    <div class='form-bubble'>
                        <strong>✨ Proper Form:</strong><br>{drill['form']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.divider()

            # 3. Stopwatch & Actions
            col_actions, col_watch = st.columns([1, 1])
            
            with col_actions:
                # Log Set Button
                if st.button(f"✅ Log Set", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
                
                # Upload Button
                st.file_uploader("📤 Upload Form Video", type=['mp4', 'mov'], key=f"up_{i}")

            with col_watch:
                st.markdown("#### ⏱️ Stopwatch")
                # If not currently running
                if i not in st.session_state.stopwatch_start:
                    if st.button("Start", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    # STOP Button (Clicking this interrupts the loop below)
                    if st.button("🛑 Stop & Save", key=f"stop_{i}", use_container_width=True):
                        elapsed = time.time() - st.session_state.stopwatch_start[i]
                        st.session_state.stopwatch_results[i] = f"{elapsed:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()
                    
                    # Live Counting Visual
                    start_time = st.session_state.stopwatch_start[i]
                    placeholder = st.empty()
                    # Run a loop to update the UI
                    while True:
                        curr_elapsed = time.time() - start_time
                        placeholder.markdown(f"<h1 style='text-align:center; color:#EF4444;'>{curr_elapsed:.1f}s</h1>", unsafe_allow_html=True)
                        time.sleep(0.1)

                # Show saved time if exists
                if i in st.session_state.stopwatch_results:
                    st.success(f"⏱️ Recorded: {st.session_state.stopwatch_results[i]}")

            # 4. Demo Video (At Bottom)
            if drill['demo'] and "http" in drill['demo']:
                st.caption("🎥 Exercise Demo")
                st.video(drill['demo'])

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        final = [{
            "Exercise": d['ex'], 
            "Sets": st.session_state.set_counts.get(idx, 0), 
            "Time": st.session_state.stopwatch_results.get(idx, "N/A")
        } for idx, d in enumerate(st.session_state.current_session)]
        
        st.session_state.archives.append({
            "date": get_now_est().strftime('%Y-%m-%d %H:%M'), 
            "sport": sport_choice, 
            "data": final
        })
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
