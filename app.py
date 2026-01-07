import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

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

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

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
    
    # Updated Sport List to include Pilates
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    
    # Updated Locations to include Floor (common for Pilates)
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

    st.markdown(f"**Date:** {get_now_est().strftime('%Y-%m-%d')}")

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
border_color = "#3B82F6" if dark_mode else "#CBD5E1"
accent_color = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    
    /* Expander Styling */
    div[data-testid="stExpander"] details summary {{
        background-color: {accent_color} !important;
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
    
    /* Metrics Styling */
    .metric-label {{ font-size: 0.75rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin-bottom: 0px; }}
    .metric-value {{ font-size: 1.1rem; color: {accent_color}; font-weight: 700; margin-top: 0px; }}
    
    h1, h2, h3, p, span {{ color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC & SCALING ---
def scale_text(val_str, multiplier):
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def extract_clean_url(text):
    """Extracts the first valid http/https URL from a string."""
    if not isinstance(text, str): return ""
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else ""

def get_csv_urls(sport, selected_envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {
        "Basketball": f"{base}basketball.csv",
        "Softball": f"{base}softball.csv",
        "Track": f"{base}track.csv",
        "Pilates": f"{base}pilates.csv", 
        "General": f"{base}general.csv"
    }
    # Load the main sport file
    load_list = [urls.get(sport, urls["General"])]
    
    # Always load general bands
    load_list += [f"{base}general-loop-band.csv", f"{base}general-mini-bands.csv"]
    
    # Conditionally load weight room files
    if "Weight Room" in selected_envs:
        load_list += [
            f"{base}barbell.csv", 
            f"{base}general-cable-crossover.csv", 
            f"{base}general-dumbell.csv", 
            f"{base}general-kettlebell.csv", 
            f"{base}general-medball.csv"
        ]
    return load_list

def load_and_build_workout(sport, multiplier, env_selections, limit):
    urls = get_csv_urls(sport, env_selections)
    all_rows = []
    
    for url in urls:
        try:
            df = pd.read_csv(url).fillna("N/A")
            # Strip whitespace from headers
            df.columns = [c.strip() for c in df.columns]
            all_rows.extend(df.to_dict('records'))
        except Exception as e:
            # Silently skip missing files
            continue
    
    if not all_rows: return []

    # CLEAN AND NORMALIZE LOCATIONS
    # This fixes the "Location" vs "Env." mismatch
    clean_envs = [s.strip().lower() for s in env_selections]
    
    filtered_pool = []
    for r in all_rows:
        # Check both column names
        row_loc = str(r.get('Env.', r.get('Location', 'General'))).strip().lower()
        
        # Keep if matches selection OR if row is labeled "all"
        if row_loc in clean_envs or "all" in row_loc:
            filtered_pool.append(r)
    
    if not filtered_pool: return []
    random.shuffle(filtered_pool)
    
    selected = []
    seen_names = set()
    
    for item in filtered_pool:
        if len(selected) >= limit: break
        
        name = item.get('Exercise Name', item.get('Exercise', 'Unknown'))
        
        # Deduplication
        if name in seen_names: continue
        seen_names.add(name)

        # Basic Scaling Logic
        base_sets = item.get('Sets', 3)
        # Handle cases where Sets might be non-numeric string
        try:
            sets_val = int(float(base_sets))
        except:
            sets_val = 3

        # Extract Raw Demo text and clean it
        raw_demo = str(item.get('Demo', item.get('Demo_URL', '')))
        clean_demo = extract_clean_url(raw_demo)

        drill = {
            "ex": name,
            "env": item.get('Env.', item.get('Location', 'General')), # Normalized return
            "category": item.get('Category', 'Skill'),
            "cns": item.get('CNS', 'Low'),
            "focus": item.get('Primary Focus', 'Performance'),
            "stars": item.get('Stars', '⭐⭐⭐'),
            "pre_req": item.get('Pre-Req', 'N/A'),
            "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', item.get('Reps', '10')), multiplier),
            "time": item.get('Time', 'N/A'),
            "hs": scale_text(item.get('HS Goals', 'N/A'), multiplier),
            "coll": scale_text(item.get('College Goals', 'N/A'), multiplier),
            "desc": item.get('Description', 'See demo for form.'),
            "proper_form": item.get('Proper Form', 'Maintain core stability and breathing.'),
            "demo": clean_demo
        }
        selected.append(drill)

        # Partner Drill Logic (Left/Right)
        side_match = re.search(r'\(L\)|\(R\)', name)
        if side_match:
            tag = "(R)" if side_match.group() == "(L)" else "(L)"
            partner_name = name.replace(side_match.group(), tag)
            
            # Find the partner in the remaining pool
            for p in filtered_pool:
                p_name = p.get('Exercise Name', p.get('Exercise', ''))
                if p_name == partner_name and p_name not in seen_names:
                    p_drill = drill.copy()
                    p_drill['ex'] = partner_name
                    selected.append(p_drill)
                    seen_names.add(partner_name)
                    break
                    
    return selected

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE WORKOUT", use_container_width=True):
    res = load_and_build_workout(sport_choice, mult, location_filter, num_drills)
    if res:
        st.session_state.current_session = res
        st.session_state.set_counts = {i: 0 for i in range(len(res))}
        st.session_state.workout_finished = False
    else:
        st.error(f"No drills found for {sport_choice} in {', '.join(location_filter)}. Try adding 'Gym' or 'General' to filters.")

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    for i, drill in enumerate(st.session_state.current_session):
        # Auto-expand the first drill
        with st.expander(f"**{i+1}. {drill['ex']}** |  {drill['stars']}", expanded=(i==0)):
            
            # Metric Grid
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>📍 Env</p><p class='metric-value'>{drill['env']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>📂 Category</p><p class='metric-value'>{drill['category']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>🧠 CNS</p><p class='metric-value'>{drill['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>🎯 Focus</p><p class='metric-value'>{drill['focus']}</p>", unsafe_allow_html=True)
            
            st.divider()
            
            m5, m6, m7, m8 = st.columns(4)
            m5.markdown(f"<p class='metric-label'>🔢 Sets</p><p class='metric-value'>{drill['sets']}</p>", unsafe_allow_html=True)
            m6.markdown(f"<p class='metric-label'>🔄 Reps/Dist</p><p class='metric-value'>{drill['reps']}</p>", unsafe_allow_html=True)
            m7.markdown(f"<p class='metric-label'>🕒 Time</p><p class='metric-value'>{drill['time']}</p>", unsafe_allow_html=True)
            m8.markdown(f"<p class='metric-label'>⚠️ Pre-Req</p><p class='metric-value'>{drill['pre_req']}</p>", unsafe_allow_html=True)

            # Goals Section
            c9, c10 = st.columns(2)
            if drill['hs'] != "N/A": c9.info(f"**HS Goal:** {drill['hs']}")
            if drill['coll'] != "N/A": c10.success(f"**College Goal:** {drill['coll']}")

            # Description
            st.write(f"**📝 Description:** {drill['desc']}")
            
            # Proper Form Check (New Feature)
            if drill['proper_form'] and drill['proper_form'] != "N/A":
                st.warning(f"**✨ Proper Form:** {drill['proper_form']}")
            
            st.divider()
            
            # Controls
            col_a, col_b = st.columns([1, 1])
            with col_a:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['sets']})", key=f"btn_{i}", use_container_width=True):
                    if curr < drill['sets']:
                        st.session_state.set_counts[i] += 1
                        st.rerun()
                
                # SAFE VIDEO RENDERING
                if drill['demo']:
                    try:
                        st.video(drill['demo'])
                    except Exception as e:
                        st.warning("Video preview unavailable.")
                        st.markdown(f"[🎥 Click to Watch on YouTube]({drill['demo']})")
                else:
                    st.caption("No video demo available.")

            with col_b:
                st.markdown("#### ⏱️ Drill / Rest Timer")
                t_val = st.number_input("Seconds", 5, 600, 60, key=f"timer_input_{i}")
                if st.button("Start Timer", key=f"timer_btn_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(int(t_val), -1, -1):
                        ph.markdown(f"<h3 style='text-align:center; color:{accent_color};'>{t}s</h3>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.markdown("<h3 style='text-align:center;'>✅ Time's Up!</h3>", unsafe_allow_html=True)
                
                st.markdown("#### 📤 Upload Form")
                st.file_uploader("Upload Clip", type=['mp4', 'mov'], key=f"file_{i}")

    st.divider()
    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.balloons()
    st.success("Workout Summary Generated!")
    
    # Simple Summary Table
    summary_data = []
    for d in st.session_state.current_session:
        summary_data.append({
            "Exercise": d['ex'],
            "Sets Planned": d['sets'],
            "Reps": d['reps'],
            "Env": d['env']
        })
    st.table(pd.DataFrame(summary_data))
    
    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()
else:
    st.info("👈 Use the sidebar to set your profile and generate a session.")
