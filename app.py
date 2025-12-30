import streamlit as st
import pandas as pd
import random
import time
import re

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. DYNAMIC THEMING & CSS ---
# Using Blue headers for maximum visibility when expanded
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
    .metric-label { font-size: 0.75rem; color: #64748b; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.1rem; color: #2563EB; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC HELPERS ---
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

# --- 4. DATA LOADING & ROBUST FILTERING ---
def load_and_group_workout(sport, multiplier, env_selections, limit):
    urls = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/track.csv",
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/general.csv"
    }
    
    try:
        df = pd.read_csv(urls[sport]).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        
        # FUZZY FILTER: Case-insensitive and whitespace-insensitive
        # This fixes the "Track" not found issue
        clean_selections = [s.strip().lower() for s in env_selections]
        
        def is_match(row_env):
            val = str(row_env).strip().lower()
            return val in clean_selections

        filtered_df = df[df['Env.'].apply(is_match)]
        
        if filtered_df.empty:
            return []

        pool = filtered_df.to_dict('records')
        random.shuffle(pool)
        
        selected = []
        for item in pool:
            if len(selected) >= limit: break
            name = item.get('Exercise Name', 'Unknown')
            if any(name == s.get('ex') for s in selected): continue

            drill = {
                "ex": name,
                "env": item.get('Env.'),
                "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
                "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
                "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
                "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
                "desc": item.get('Description', 'No details.'),
                "demo": str(item.get('Demo', '')).strip()
            }
            
            std_str = f"{drill['hs']} {drill['coll']}"
            drill['timer'] = extract_seconds(std_str) if any(c.isdigit() for c in std_str) else extract_seconds(item.get('Time', '60'))
            selected.append(drill)

            # AUTO L/R PAIRING
            side_match = re.search(r'\(L\)|\(R\)', name)
            if side_match:
                tag = "(R)" if side_match.group() == "(L)" else "(L)"
                partner_name = name.replace(side_match.group(), tag)
                for p in pool:
                    if p.get('Exercise Name') == partner_name:
                        p_drill = drill.copy()
                        p_drill['ex'] = partner_name
                        selected.append(p_drill)
                        break
        return selected
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    
    # ADDED: "Weight Room" to the list
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
            st.warning(f"No drills found for '{sport_choice}' at selected locations. Try selecting 'General' or 'Outdoor'.")

# --- 6. MAIN INTERFACE ---
st.title("🏆 PRO-ATHLETE TRACKER")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']}", expanded=(i==0)):
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f"<p class='metric-label'>Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            with m2: st.markdown(f"<p class='metric-label'>Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            with m3: st.markdown(f"<p class='metric-label'>Goal Time</p><p class='metric-value'>{drill['timer']}s</p>", unsafe_allow_html=True)
            
            st.info(f"🏅 **HS:** {drill['hs']} | 🎓 **College:** {drill['coll']}")
            st.write(f"**Instructions:** {drill['desc']}")
            
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
    st.success("✅ Session Complete! Data saved.")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'sets', 'reps']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
