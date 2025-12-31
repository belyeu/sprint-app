import streamlit as st
import pandas as pd
import random
import time
import re

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Performance", layout="wide", page_icon="🏆")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "hs_goal": "State Championship",
        "college_goal": "D1 Recruitment"
    }
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. IMAGE ASSETS ---
IMAGE_ASSETS = {
    "Softball": ["IMG_3874.jpeg", "IMG_3875.jpeg"],
    "General": ["IMG_3876.jpeg", "IMG_3877.jpeg"],
    "Track": ["IMG_3881.jpeg"]
}

# --- 3. DYNAMIC THEMING & CSS ---
st.markdown("""
    <style>
    /* Expander Header Visibility Fix */
    div[data-testid="stExpander"] details summary {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    div[data-testid="stExpander"] details summary svg { fill: white !important; }
    
    /* Card Styling */
    div[data-testid="stExpander"] {
        border: 1px solid #2563EB44 !important;
        border-radius: 12px !important;
        border-top: none !important;
    }

    .metric-label { font-size: 0.75rem; color: #64748b; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 1.1rem; color: #2563EB; font-weight: 700; margin-bottom: 8px; }
    
    div.stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        font-weight: 600 !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC HELPERS ---
def get_csv_urls(selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    # Universal equipment (All Locations)
    files = ["general-loop-band.csv", "general-mini-bands.csv"]
    
    # Weight Room Specifics
    if "Weight Room" in selected_envs:
        files += [
            "barbell.csv", "general-cable-crossover.csv", 
            "general-dumbell.csv", "general-kettlebell.csv", "general-medball.csv"
        ]
    return [base + f for f in files]

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
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

# --- 5. WORKOUT GENERATOR ---
def load_and_pair_workout(multiplier, env_selections, limit):
    urls = get_csv_urls(env_selections)
    all_rows = []
    
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
            
    if not all_rows: return []
    
    random.shuffle(all_rows)
    selected = []
    
    for item in all_rows:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        if any(name == s.get('ex') for s in selected): continue

        drill = {
            "ex": name,
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'Perform with explosive intent.'),
            "demo": str(item.get('Demo', '')).strip(),
            "img": random.choice(IMAGE_ASSETS["General"])
        }
        
        # Standards-based Timer
        std_str = f"{drill['hs']} {drill['coll']}"
        drill['timer'] = extract_seconds(std_str) if any(c.isdigit() for c in std_str) else extract_seconds(item.get('Time', '60'))
        
        selected.append(drill)

        # L/R Auto-Pairing
        side_match = re.search(r'\(L\)|\(R\)', name)
        if side_match:
            tag = "(R)" if side_match.group() == "(L)" else "(L)"
            partner_name = name.replace(side_match.group(), tag)
            for p in all_rows:
                p_name = p.get('Exercise Name', p.get('Exercise', ''))
                if p_name == partner_name:
                    p_drill = drill.copy()
                    p_drill['ex'] = partner_name
                    selected.append(p_drill)
                    break
    return selected

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("🎨 INTERFACE")
    dark = st.toggle("Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Update Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    envs = st.multiselect("Location", ["Weight Room", "Gym", "Field", "Track", "Cages"], default=["Weight Room"])
    num = st.slider("Exercises", 5, 20, 12)
    effort = st.select_slider("Intensity", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        st.session_state.current_session = load_and_pair_workout(mult, envs, num)
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

# --- 7. MAIN UI ---
st.title("🏆 PRO-ATHLETE TRACKER")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(drill['img'], use_container_width=True)
            with col2:
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<p class='metric-label'>Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
                m2.markdown(f"<p class='metric-label'>Reps</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
                m3.markdown(f"<p class='metric-label'>Standard</p><p class='metric-value'>{drill['timer']}s</p>", unsafe_allow_html=True)
                
                st.info(f"🏅 **HS Goal:** {drill['hs']} | 🎓 **College:** {drill['coll']}")
                st.write(f"**Focus:** {drill['desc']}")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts[i]
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"l_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo'].startswith('http'): st.video(drill['demo'])
            
            with c2:
                if st.button(f"⏱️ Start {drill['timer']}s Timer", key=f"t_{i}"):
                    ph = st.empty()
                    for t in range(drill['timer'], -1, -1):
                        ph.metric("Drill Timer", f"{t}s")
                        time.sleep(1)
                    st.balloons()
                
                st.file_uploader("Upload Form Clip", type=['mp4','mov'], key=f"v_{i}")

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Session Complete! Data Logged.")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'sets', 'reps']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👋 Select locations and build your workout in the sidebar.")import streamlit as st
import pandas as pd
import random
import time
import re

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Elite Athlete Tracker", layout="wide", page_icon="🏋️")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. THEME & UI ---
st.markdown("""
    <style>
    div[data-testid="stExpander"] details summary {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #2563EB44 !important;
        border-radius: 12px !important;
        margin-bottom: 15px;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 1.1rem; color: #2563EB; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING LOGIC ---
def get_csv_urls(selected_envs):
    """Maps selected locations to specific CSV data sources."""
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    
    # Files that apply to EVERY location
    files_to_load = ["general-loop-band.csv", "general-mini-bands.csv"]
    
    # Files specific to the Weight Room
    if "Weight Room" in selected_envs:
        files_to_load += [
            "barbell.csv", 
            "general-cable-crossover.csv", 
            "general-dumbell.csv", 
            "general-kettlebell.csv", 
            "general-medball.csv"
        ]
    
    return [base_url + f for f in files_to_load]

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
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def load_athlete_workout(multiplier, env_selections, limit):
    urls = get_csv_urls(env_selections)
    all_data = []
    
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_data.append(df)
        except:
            continue
            
    if not all_data: return []
    
    full_df = pd.concat(all_data, ignore_index=True)
    pool = full_df.to_dict('records')
    random.shuffle(pool)
    
    selected = []
    for item in pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        
        if any(name == s.get('ex') for s in selected): continue

        drill = {
            "ex": name,
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See video for form.'),
            "demo": str(item.get('Demo', '')).strip()
        }
        
        # Priority Timer: Check Standards first, then Time column
        std_str = f"{drill['hs']} {drill['coll']}"
        drill['timer'] = extract_seconds(std_str) if any(c.isdigit() for c in std_str) else extract_seconds(item.get('Time', '60'))
        
        selected.append(drill)

        # L/R Grouping
        side_match = re.search(r'\(L\)|\(R\)', name)
        if side_match:
            tag = "(R)" if side_match.group() == "(L)" else "(L)"
            partner_name = name.replace(side_match.group(), tag)
            for p in pool:
                p_name = p.get('Exercise Name', p.get('Exercise', ''))
                if p_name == partner_name:
                    p_drill = drill.copy()
                    p_drill['ex'] = partner_name
                    selected.append(p_drill)
                    break
                    
    return selected

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🏋️ TRAINING SETUP")
    location_filter = st.multiselect(
        "Current Location", 
        ["Weight Room", "Gym", "Field", "Track", "Cages"],
        default=["Weight Room"]
    )
    num_drills = st.slider("Session Volume", 5, 20, 10)
    effort = st.select_slider("Intensity Meter", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

    if st.button("🚀 BUILD WORKOUT", use_container_width=True):
        res = load_athlete_workout(mult, location_filter, num_drills)
        if res:
            st.session_state.current_session = res
            st.session_state.set_counts = {i: 0 for i in range(len(res))}
            st.session_state.workout_finished = False
        else:
            st.error("Check connection or CSV filenames.")

# --- 5. MAIN UI ---
st.title("🏆 PRO-ATHLETE PERFORMANCE")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']}", expanded=(i==0)):
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f"<p class='metric-label'>Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            with m2: st.markdown(f"<p class='metric-label'>Reps</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            with m3: st.markdown(f"<p class='metric-label'>Goal Timer</p><p class='metric-value'>{drill['timer']}s</p>", unsafe_allow_html=True)
            
            st.info(f"🏅 **Standards:** HS: {drill['hs']} | College: {drill['coll']}")
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts[i]
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"log_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo'].startswith('http'): st.video(drill['demo'])
            with c2:
                if st.button(f"⏱️ Start {drill['timer']}s Drill Timer", key=f"t_{i}"):
                    ph = st.empty()
                    for t in range(drill['timer'], -1, -1):
                        ph.metric("Timer Active", f"{t}s")
                        time.sleep(1)
                    st.balloons()

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Session Complete! Standards met.")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'sets', 'reps']])
    if st.button("Restart"):
        st.session_state.current_session = None
        st.rerun()

