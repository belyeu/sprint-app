import streamlit as st
import pandas as pd
import random
import time
import re

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

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
    div[data-testid="stExpander"] details summary {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    div[data-testid="stExpander"] details summary svg { fill: white !important; }
    div[data-testid="stExpander"] {
        border: 1px solid #2563EB44 !important;
        border-radius: 12px !important;
        border-top: none !important;
    }
    .metric-label { font-size: 0.75rem; color: #64748b; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.1rem; color: #2563EB; font-weight: 700; }
    div.stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        font-weight: 600 !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC HELPERS ---
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

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    # Start with sport-specific core file
    urls = {
        "Basketball": f"{base}basketball.csv",
        "Softball": f"{base}softball.csv",
        "Track": f"{base}track.csv",
        "General": f"{base}general.csv"
    }
    load_list = [urls[sport]]
    
    # Universal Equipment (Available everywhere)
    load_list += [f"{base}general-loop-band.csv", f"{base}general-mini-bands.csv"]
    
    # Specialized Weight Room Tables
    if "Weight Room" in selected_envs:
        load_list += [
            f"{base}barbell.csv", 
            f"{base}general-cable-crossover.csv", 
            f"{base}general-dumbell.csv", 
            f"{base}general-kettlebell.csv", 
            f"{base}general-medball.csv"
        ]
    return load_list

# --- 5. DATA LOADING & ROBUST FILTERING ---
def load_and_group_workout(sport, multiplier, env_selections, limit):
    urls = get_csv_urls(sport, env_selections)
    all_rows = []
    
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue

    if not all_rows: return []

    # Filter by selected environments
    clean_selections = [s.strip().lower() for s in env_selections]
    filtered_pool = [
        row for row in all_rows 
        if str(row.get('Env.', 'General')).strip().lower() in clean_selections
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
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'No details.'),
            "demo": str(item.get('Demo', '')).strip(),
            "img": random.choice(IMAGE_ASSETS.get(sport, IMAGE_ASSETS["General"]))
        }
        
        std_str = f"{drill['hs']} {drill['coll']}"
        drill['timer'] = extract_seconds(std_str) if any(c.isdigit() for c in std_str) else extract_seconds(item.get('Time', '60'))
        selected.append(drill)

        # L/R Auto-Pairing
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

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Update Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect(
        "Facility Location", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "General"],
        default=["Gym", "Field"]
    )
    
    num_drills = st.slider("Target Drills", 5, 20, 12)
    effort = st.select_slider("Intensity Meter", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        workout = load_and_group_workout(sport_choice, mult, location_filter, num_drills)
        if workout:
            st.session_state.current_session = workout
            st.session_state.set_counts = {i: 0 for i in range(len(workout))}
            st.session_state.workout_finished = False
        else:
            st.warning("No drills found. Try adding 'General' or 'Weight Room' to your locations.")

# --- 7. MAIN INTERFACE ---
st.title("🏆 PRO-ATHLETE TRACKER")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']}", expanded=(i==0)):
            col_img, col_data = st.columns([1, 2])
            with col_img:
                st.image(drill['img'], use_container_width=True)
            with col_data:
                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f"<p class='metric-label'>Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
                with m2: st.markdown(f"<p class='metric-label'>Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
                with m3: st.markdown(f"<p class='metric-label'>Goal Time</p><p class='metric-value'>{drill['timer']}s</p>", unsafe_allow_html=True)
            
                st.info(f"🏅 **HS Goal:** {drill['hs']} | 🎓 **College:** {drill['coll']}")
                st.write(f"**Description:** {drill['desc']}")
            
            st.divider()
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
                st.file_uploader("Upload Form Video", type=['mp4', 'mov'], key=f"v_{i}")

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("✅ Session Complete! Data saved.")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'sets', 'reps']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
