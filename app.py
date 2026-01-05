import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete", 
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

# --- 2. SIDEBAR & FILTERS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Goals"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["hs_goal"] = st.text_input("HS Goal", st.session_state.user_profile["hs_goal"])
        st.session_state.user_profile["college_goal"] = st.text_input("College Goal", st.session_state.user_profile["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect(
        "Facility Location (Env.)", 
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"],
        default=["Gym", "Floor"]
    )
    num_drills = st.slider("Target Drills", 5, 20, 13)
    
    st.divider()
    st.header("📊 INTENSITY METER")
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING & BUTTON VISIBILITY ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
border_color = "#3B82F6" if dark_mode else "#CBD5E1"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* FIX BUTTON VISIBILITY: High contrast Blue/White */
    .stButton > button {{
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #1D4ED8 !important;
        font-weight: 700 !important;
        width: 100% !important;
        display: block !important;
    }}
    .stButton > button:hover {{
        background-color: #1D4ED8 !important;
        border: 1px solid #1E40AF !important;
    }}

    div[data-testid="stExpander"] details summary {{
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    div[data-testid="stExpander"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {border_color} !important; 
        border-radius: 12px !important; 
        border-top: none !important;
    }}
    .field-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin-bottom: -5px;}}
    .field-value {{ font-size: 1rem; color: #3B82F6; font-weight: 700; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
def extract_seconds(text):
    text = str(text).lower()
    m_ss = re.search(r'(\d+):(\d+)', text)
    if m_ss: return int(m_ss.group(1)) * 60 + int(m_ss.group(2))
    ss = re.search(r'(\d+)\s*(s|sec)', text)
    if ss: return int(ss.group(1))
    fallback = re.search(r'\d+', text)
    return int(fallback.group()) if fallback else 60

def scale_text(val_str, multiplier, is_reps=False):
    val_str = str(val_str)
    if is_reps and (val_str.upper() == "N/A" or val_str.strip() == ""): return "10"
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {"Basketball": f"{base}basketball.csv", "Softball": f"{base}softball.csv", 
            "Track": f"{base}track.csv", "Pilates": f"{base}pilates.csv", "General": f"{base}general.csv"}
    load_list = [urls.get(sport, urls["General"])]
    load_list += [f"{base}general-loop-band.csv", f"{base}general-mini-bands.csv"]
    if "Weight Room" in selected_envs:
        load_list += [f"{base}barbell.csv", f"{base}general-cable-crossover.csv", f"{base}general-dumbell.csv", f"{base}general-kettlebell.csv", f"{base}general-medball.csv"]
    return load_list

def load_and_build_workout(sport, multiplier, env_selections, limit):
    urls = get_csv_urls(sport, env_selections)
    all_rows = []
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except: continue
    
    clean_envs = [s.strip().lower() for s in env_selections]
    filtered_pool = [r for r in all_rows if str(r.get('Env.', 'General')).strip().lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    if not filtered_pool: return []
    random.shuffle(filtered_pool)
    
    selected = []
    for item in filtered_pool:
        if len(selected) >= limit: break
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        
        hs_goal_text = item.get('HS Goals', 'N/A')
        time_val = item.get('Time Goal', item.get('Time', 'N/A'))
        drill_s = extract_seconds(hs_goal_text if time_val == "N/A" else time_val)
        rest_s = extract_seconds(item.get('Rest Time', '60s'))

        drill = {
            "rank": item.get('Rank', 'N/A'),
            "ex": name,
            "level": item.get('Level', 'N/A'),
            "env": item.get('Env.', 'General'),
            "muscle": item.get('Primary Muscle', 'N/A'),
            "cns": item.get('CNS', 'Low'),
            "sets": int(round(int(item.get('Sets', 3) if str(item.get('Sets')).isdigit() else 3) * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier, is_reps=True),
            "drill_timer": drill_s,
            "rest_timer": rest_s,
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "hs": scale_text(hs_goal_text, multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'N/A'),
            "proper_form": item.get('Proper Form', 'N/A'),
            "demo": str(item.get('Demo', '')).strip(),
            "category": item.get('Category', 'Skill')
        }
        selected.append(drill)
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.workout_finished = False

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)



if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**#{drill['rank']} {drill['ex']}** | {drill['stars']}", expanded=(i==0)):
            # TECHNICAL FIELDS 1-17
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<p class='field-label'>Rank</p><p class='field-value'>{drill['rank']}</p>", unsafe_allow_html=True)
            c2.markdown(f"<p class='field-label'>Level</p><p class='field-value'>{drill['level']}</p>", unsafe_allow_html=True)
            c3.markdown(f"<p class='field-label'>Env</p><p class='field-value'>{drill['env']}</p>", unsafe_allow_html=True)
            c4.markdown(f"<p class='field-label'>Muscle</p><p class='field-value'>{drill['muscle']}</p>", unsafe_allow_html=True)

            c5, c6, c7, c8 = st.columns(4)
            c5.markdown(f"<p class='field-label'>CNS</p><p class='field-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            c6.markdown(f"<p class='field-label'>Sets</p><p class='field-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            c7.markdown(f"<p class='field-label'>Reps/Dist</p><p class='field-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            c8.markdown(f"<p class='field-label'>Category</p><p class='field-value'>{drill['category']}</p>", unsafe_allow_html=True)

            c9, c10, c11, c12 = st.columns(4)
            c9.markdown(f"<p class='field-label'>Focus</p><p class='field-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            c10.markdown(f"<p class='field-label'>Pre-Req</p><p class='field-value'>{drill['pre_req']}</p>", unsafe_allow_html=True)
            c11.markdown(f"<p class='field-label'>Drill (s)</p><p class='field-value'>{drill['drill_timer']}</p>", unsafe_allow_html=True)
            c12.markdown(f"<p class='field-label'>Rest (s)</p><p class='field-value'>{drill['rest_timer']}</p>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            g1.info(f"**HS Goal:** {drill['hs']}")
            g2.success(f"**College Goal:** {drill['coll']}")

            st.write(f"**📝 Description:** {drill['desc']}")
            st.warning(f"**✨ Proper Form:** {drill['proper_form']}")
            
            st.divider()
            
            # Interactive Area with 3-Column Layout
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"log_{i}"):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                if drill['demo'] and "http" in drill['demo']: st.video(drill['demo'])

            with col_b:
                st.markdown("#### ⚡ Drill Timer")
                d_in = st.number_input("Seconds", 1, 600, drill['drill_timer'], key=f"di_{i}")
                d_ph = st.empty()
                if st.button("Start Drill", key=f"db_{i}"):
                    for t in range(int(d_in), -1, -1):
                        d_ph.metric("Action", f"{t}s")
                        time.sleep(1)
                    st.toast("Drill Complete!")

            with col_c:
                st.markdown("#### 🛌 Rest Timer")
                r_in = st.number_input("Seconds", 1, 600, drill['rest_timer'], key=f"ri_{i}")
                r_ph = st.empty()
                if st.button("Start Rest", key=f"rb_{i}"):
                    for t in range(int(r_in), -1, -1):
                        r_ph.metric("Rest", f"{t}s")
                        time.sleep(1)
                    st.toast("Rest Over!", icon="🔔")

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Workout Summary")
    summary_df = pd.DataFrame(st.session_state.current_session)
    # Corrected column keys to match data mapping
    st.table(summary_df[['ex', 'env', 'category', 'sets', 'reps']])
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
else:
    st.info("👈 Use the sidebar to generate your session.")
