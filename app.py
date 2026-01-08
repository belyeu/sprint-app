import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# Initialize all session states
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'archives' not in st.session_state:
    st.session_state.archives = [] 
if 'view_archive_index' not in st.session_state:
    st.session_state.view_archive_index = None
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'stopwatch_start' not in st.session_state:
    st.session_state.stopwatch_start = {}
if 'stopwatch_times' not in st.session_state:
    st.session_state.stopwatch_times = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "age": 17,
        "weight": 180,
        "goal_weight": 190,
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }

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
            st.session_state.view_archive_index = archive_names.index(selected_arch)
        else:
            st.session_state.view_archive_index = None
    else:
        st.caption("No archived workouts yet.")

    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["weight"] = st.number_input("Weight (lbs)", value=st.session_state.user_profile["weight"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Floor"])
    
    num_drills = st.slider("Target Drills", 5, 20, 13)
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_color = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    /* Summary Table Visibility */
    .stTable, [data-testid="stMarkdownContainer"] p, h1, h2, h3 {{ color: {text_color} !important; }}
    thead tr th {{ color: {text_color} !important; background-color: {accent_color}; }}
    div[data-testid="stExpander"] details summary {{ background-color: {accent_color} !important; color: white !important; border-radius: 8px; padding: 0.6rem 1rem; }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border: 1px solid {accent_color} !important; border-radius: 12px !important; }}
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
    random.shuffle(filtered_pool)
    
    selected = []
    seen = set()
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if name in seen: continue
        seen.add(name)
        
        selected.append({
            "ex": name, "category": item.get('Category', 'Skill'),
            "sets": int(round(int(float(item.get('Sets', 3))) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', '10'), multiplier),
            "desc": item.get('Description', 'Maintain form.'),
            "form": item.get('Proper Form', 'Keep core tight.'),
            "demo": str(item.get('Demo', item.get('Demo_URL', '')))
        })
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.stopwatch_times = {}
        st.session_state.stopwatch_start = {}
        st.session_state.workout_finished = False
        st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.view_archive_index is not None:
    arch = st.session_state.archives[st.session_state.view_archive_index]
    st.info(f"📁 Viewing Archive: {arch['date']}")
    st.table(pd.DataFrame(arch['data']))
    if st.button("Close Archive"):
        st.session_state.view_archive_index = None
        st.rerun()

elif st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{i+1}. {drill['ex']}** ({st.session_state.set_counts.get(i,0)}/{drill['sets']})", expanded=(i==0)):
            m1, m2 = st.columns(2)
            m1.markdown(f"<p class='metric-label'>🔢 Target Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            
            st.write(f"**📝 Instructions:** {drill['desc']}")
            st.warning(f"**✨ Proper Form:** {drill['form']}")
            st.divider()
            
            col_log, col_sw = st.columns(2)
            with col_log:
                if st.button(f"✅ Log Set", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] = st.session_state.set_counts.get(i, 0) + 1
                    st.rerun()
            
            with col_sw:
                if i not in st.session_state.stopwatch_start:
                    if st.button("⏱️ Start Stopwatch", key=f"start_{i}", use_container_width=True):
                        st.session_state.stopwatch_start[i] = time.time()
                        st.rerun()
                else:
                    elapsed = time.time() - st.session_state.stopwatch_start[i]
                    st.markdown(f"<h2 style='text-align:center;'>{elapsed:.1f}s</h2>", unsafe_allow_html=True)
                    if st.button("🛑 Stop & Save", key=f"stop_{i}", use_container_width=True):
                        st.session_state.stopwatch_times[i] = f"{elapsed:.1f}s"
                        del st.session_state.stopwatch_start[i]
                        st.rerun()
                
                if i in st.session_state.stopwatch_times:
                    st.success(f"Time: {st.session_state.stopwatch_times[i]}")

            # Demo Video at bottom
            if drill['demo'] and "http" in drill['demo']:
                st.divider()
                st.caption("🎥 Exercise Demo")
                st.video(drill['demo'])

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        summary = [{"Exercise": d['ex'], "Sets": st.session_state.set_counts.get(idx, 0), "Time": st.session_state.stopwatch_times.get(idx, "N/A")} for idx, d in enumerate(st.session_state.current_session)]
        st.session_state.archives.append({"date": get_now_est().strftime('%Y-%m-%d %H:%M'), "sport": sport_choice, "data": summary})
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.header("📊 Session Summary")
    summary_df = pd.DataFrame(st.session_state.archives[-1]['data'])
    st.table(summary_df)
    if st.button("Start New Session", use_container_width=True):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()

else:
    # --- OPENING INSTRUCTIONS ---
    st.info("👋 **Welcome to the Elite Performance Tracker**")
    st.markdown("""
    ### 🏁 Getting Started:
    1. **Set Profile:** Check your HS and College goals in the sidebar.
    2. **Filter Session:** Choose your **Sport** and **Location** (e.g., Floor, Weight Room).
    3. **Intensity:** Use the **Intensity Meter** to scale reps.
    4. **Generate:** Click the big button in the sidebar to load your drills.
    
    *Workouts are automatically saved and accessible in the 'History' tab.*
    """)
