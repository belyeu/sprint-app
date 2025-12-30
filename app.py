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
    st.session_state.user_profile = {"name": "Elite Athlete", "hs_goal": "State Standard", "college_goal": "D1 Standard"}
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. THEME & CSS ---
dark_mode = st.sidebar.toggle("Dark Mode", value=True)
if dark_mode:
    primary_bg, card_bg, text_color, accent = "#0F172A", "#1E293B", "#F8FAFC", "#3B82F6"
else:
    primary_bg, card_bg, text_color, accent = "#FFFFFF", "#F1F5F9", "#0F172A", "#2563EB"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    div[data-testid="stExpander"] details summary {{
        background-color: {accent} !important; color: white !important;
        border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 10px;
    }}
    div[data-testid="stExpander"] {{
        background-color: {card_bg} !important; border: 1px solid {accent}44 !important; border-radius: 12px !important;
    }}
    .metric-label {{ font-size: 0.75rem; color: {accent}; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1rem; font-weight: 600; margin-bottom: 12px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def extract_time(text):
    """Extracts seconds from strings like '60s', '1:00', or '10 seconds'."""
    text = str(text).lower()
    # Check for M:SS format
    m_ss = re.search(r'(\d+):(\d+)', text)
    if m_ss:
        return int(m_ss.group(1)) * 60 + int(m_ss.group(2))
    # Check for SSs format
    ss = re.search(r'(\d+)\s*(s|sec|second)', text)
    if ss:
        return int(ss.group(1))
    # Fallback to any number
    fallback = re.search(r'\d+', text)
    return int(fallback.group()) if fallback else 60

def scale_text(val_str, multiplier):
    """Scales numbers found inside a string based on intensity."""
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

# --- 4. DATA LOADING & L/R GROUPING ---
def load_and_group_data(sport, multiplier, envs, limit):
    urls = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
        "Softball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/softball.csv",
        "Track": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/track.csv",
        "General": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/general.csv"
    }
    try:
        df = pd.read_csv(urls[sport]).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        pool = df[df['Env.'].str.strip().isin(envs)].to_dict('records')
        
        if not pool: return []

        selected = []
        pool_indices = list(range(len(pool)))
        random.shuffle(pool_indices)

        for idx in pool_indices:
            if len(selected) >= limit: break
            item = pool[idx]
            name = item.get('Exercise Name', '')
            
            # Skip if already added (as part of an L/R pair)
            if any(name == s.get('Exercise Name') for s in selected): continue

            # Scale Metrics
            item['adj_sets'] = int(round(int(item.get('Sets', 3)) * multiplier))
            item['adj_reps'] = scale_text(item.get('Reps/Dist', 'N/A'), multiplier)
            
            # Set Timer based on Standards (HS or College)
            std_text = f"{item.get('HS Goals', '')} {item.get('College Goals', '')}"
            item['drill_timer'] = extract_time(std_text) if any(char.isdigit() for char in std_text) else extract_time(item.get('Time', '60'))

            selected.append(item)

            # --- AUTO L/R PAIRING ---
            side_match = re.search(r'\(L\)|\(R\)', name)
            if side_match:
                other_side = "(R)" if side_match.group() == "(L)" else "(L)"
                partner_name = name.replace(side_match.group(), other_side)
                
                # Look for partner in pool
                for partner in pool:
                    if partner.get('Exercise Name') == partner_name:
                        partner['adj_sets'] = item['adj_sets']
                        partner['adj_reps'] = item['adj_reps']
                        partner['drill_timer'] = item['drill_timer']
                        selected.append(partner)
                        break
        return selected
    except: return []

# --- 5. SIDEBAR & GEN ---
with st.sidebar:
    st.header("📍 FILTERS")
    sport = st.selectbox("Sport", ["Basketball", "Softball", "Track", "General"])
    envs = st.multiselect("Environment", ["Gym", "Field", "Cages", "Track", "Outdoor"], default=["Gym", "Field"])
    num = st.slider("Exercises", 5, 20, 10)
    effort = st.select_slider("Intensity", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        st.session_state.current_session = load_and_group_data(sport, mult, envs, num)
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

# --- 6. MAIN UI ---
st.title("🏆 PRO-ATHLETE TRACKER")

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['Exercise Name']} | {drill.get('Stars', '⭐⭐⭐')}", expanded=(i==0)):
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<p class='metric-label'>Target Sets</p><p class='metric-value'>{drill['adj_sets']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>Reps/Dist</p><p class='metric-value'>{drill['adj_reps']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>Standard Time</p><p class='metric-value'>{drill['drill_timer']}s</p>", unsafe_allow_html=True)
            
            st.info(f"**HS Standard:** {drill.get('HS Goals')} | **College Standard:** {drill.get('College Goals')}")
            st.write(f"**Description:** {drill.get('Description')}")

            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['adj_sets']})", key=f"log_{i}"):
                    if curr < drill['adj_sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
            with c2:
                if st.button(f"⏱️ Start {drill['drill_timer']}s Timer", key=f"t_{i}"):
                    ph = st.empty()
                    for t in range(drill['drill_timer'], -1, -1):
                        ph.metric("Drill Timer", f"{t}s")
                        time.sleep(1)
                    st.toast("Time Complete!")

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Workout Complete! Summary:")
    st.table(pd.DataFrame(st.session_state.current_session)[['Exercise Name', 'adj_sets', 'adj_reps']])
    if st.button("Restart"):
        st.session_state.current_session = None
        st.rerun()
