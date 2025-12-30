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

# --- 2. IMAGE MAPPING ---
IMAGE_ASSETS = {
    "Softball": ["IMG_3874.jpeg", "IMG_3875.jpeg"],
    "General": ["IMG_3876.jpeg", "IMG_3877.jpeg"],
    "Track": ["IMG_3881.jpeg"]
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🎨 INTERFACE")
    dark_mode = st.toggle("Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Update Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor"],
        default=["Gym", "Field"]
    )
    num_drills = st.slider("Number of Exercises", 5, 20, 13)

    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    intensity_mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}
    st.progress(intensity_mult[effort] / 1.5)

# --- 4. DYNAMIC THEMING & CSS ---
if dark_mode:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#0F172A", "#1E293B", "#F8FAFC", "#94A3B8", "#3B82F6", "#FFFFFF"
else:
    primary_bg, card_bg, text_color, sub_text, accent, btn_text = "#FFFFFF", "#F1F5F9", "#0F172A", "#475569", "#2563EB", "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    div[data-testid="stExpander"] details summary {{
        background-color: {accent} !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-bottom: 10px;
    }}
    
    div[data-testid="stExpander"] details summary svg {{ fill: white !important; color: white !important; }}
    
    div[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 1px solid {accent}44 !important;
        border-radius: 12px !important;
        border-top: none !important;
    }}

    div.stButton > button {{
        background-color: {accent} !important;
        color: {btn_text} !important;
        font-weight: 600 !important;
        width: 100%;
    }}

    .metric-label {{ font-size: 0.75rem; color: {sub_text}; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 1rem; color: {accent}; font-weight: 600; margin-bottom: 12px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. HELPERS: SCALING & TIMERS ---
def extract_seconds(text):
    text = str(text).lower()
    m_ss = re.search(r'(\d+):(\d+)', text)
    if m_ss: return int(m_ss.group(1)) * 60 + int(m_ss.group(2))
    ss = re.search(r'(\d+)\s*(s|sec)', text)
    if ss: return int(ss.group(1))
    fallback = re.search(r'\d+', text)
    return int(fallback.group()) if fallback else 60

def scale_text_numbers(val_str, multiplier):
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

# --- 6. DATA LOADING & L/R GROUPING ---
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
        
        # Strict Env Filter
        full_pool = df.to_dict('records')
        filtered_pool = [r for r in full_pool if str(r.get('Env.', '')).strip() in envs]
        
        if not filtered_pool: return []

        selected = []
        random.shuffle(filtered_pool)

        for item in filtered_pool:
            if len(selected) >= limit: break
            name = item.get('Exercise Name', 'Unknown')
            
            # Skip if already handled by L/R pairing
            if any(name == s.get('ex') for s in selected): continue

            # Create Drill Object
            drill = {
                "ex": name,
                "env": str(item.get('Env.', 'General')).strip(),
                "stars": item.get('Stars', '⭐⭐⭐'),
                "desc": item.get('Description', 'No details.'),
                "demo": str(item.get('Demo', '')).strip(),
                "hs_goals": scale_text_numbers(item.get('HS Goals', 'N/A'), multiplier),
                "college_goals": scale_text_numbers(item.get('College Goals', 'N/A'), multiplier),
                "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
                "reps": scale_text_numbers(item.get('Reps/Dist', 'N/A'), multiplier),
                "category": item.get('Category', 'Athleticism'),
                "static_img": random.choice(IMAGE_ASSETS.get(sport, [""])) if IMAGE_ASSETS.get(sport) else ""
            }
            
            # Timer Logic: HS/College Standard Priority
            std_text = f"{drill['hs_goals']} {drill['college_goals']}"
            drill['time_val'] = extract_seconds(std_text) if any(c.isdigit() for c in std_text) else extract_seconds(item.get('Time', '60'))

            selected.append(drill)

            # L/R Pairing
            side_match = re.search(r'\(L\)|\(R\)', name)
            if side_match:
                other = "(R)" if side_match.group() == "(L)" else "(L)"
                partner_name = name.replace(side_match.group(), other)
                for p in filtered_pool:
                    if p.get('Exercise Name') == partner_name:
                        p_drill = drill.copy()
                        p_drill['ex'] = partner_name
                        selected.append(p_drill)
                        break
        return selected
    except: return []

# --- 7. GENERATION LOGIC ---
with st.sidebar:
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        res = load_and_group_data(sport_choice, intensity_mult[effort], location_filter, num_drills)
        if res:
            st.session_state.current_session = res
            st.session_state.set_counts = {i: 0 for i in range(len(res))}
            st.session_state.workout_finished = False
        else:
            st.error("No exercises found for this environment.")

# --- 8. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center; color: {accent};'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"{drill['ex']} | {drill['stars']}", expanded=(i==0)):
            col_img, col_meta = st.columns([1, 2])
            with col_img:
                if drill['static_img']: st.image(drill['static_img'], use_container_width=True)
                else: st.markdown("🖼️ *Preview Unavailable*")

            with col_meta:
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<div class='metric-label'>Environment</div><div class='metric-value'>{drill['env']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Category</div><div class='metric-value'>{drill['category']}</div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-label'>Sets</div><div class='metric-value'>{drill['sets']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Reps/Dist</div><div class='metric-value'>{drill['reps']}</div>", unsafe_allow_html=True)

            st.divider()
            g1, g2 = st.columns(2)
            g1.info(f"**HS Standard:** {drill['hs_goals']}")
            g2.success(f"**College Standard:** {drill['college_goals']}")
            st.write(f"**Instructions:** {drill['desc']}")
            
            with st.expander("📤 Upload My Form"):
                st.file_uploader(f"Upload for {drill['ex']}", type=['mp4','jpg','png'], key=f"u_{i}")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}"):
                    if curr < drill['sets']:
                        # Auto-Rest Timer (uses the standard time)
                        t_ph = st.empty()
                        if curr + 1 < drill['sets']:
                            for t in range(drill['time_val'], -1, -1):
                                t_ph.metric(f"🛑 Resting...", f"{t}s")
                                time.sleep(1)
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                if drill['demo'].startswith('http'): st.video(drill['demo'])

            with c2:
                st.markdown("#### ⏱️ Drill Timer")
                if st.button(f"Start {drill['time_val']}s Countdown", key=f"t_btn_{i}"):
                    ph = st.empty()
                    for t in range(drill['time_val'], -1, -1):
                        ph.metric("Timer", f"{t}s")
                        time.sleep(1)
                    st.balloons()

    if st.button("🏁 FINISH SESSION", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.header("📝 Session Summary")
    st.table(pd.DataFrame(st.session_state.current_session)[['ex', 'sets', 'reps']])
    if st.button("Restart Dashboard"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👋 Use the sidebar to generate your athlete session.")
