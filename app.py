import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz
import io

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# Initialize Session States
if 'archives' not in st.session_state:
    st.session_state.archives = [] 
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'warmup_drills' not in st.session_state:
    st.session_state.warmup_drills = None
if 'stopwatch_runs' not in st.session_state:
    st.session_state.stopwatch_runs = {}
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False
if 'uploaded_media' not in st.session_state:
    st.session_state.uploaded_media = {}

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

# Helper function to check if a URL is actually a video Streamlit can play
def is_playable_video(url):
    if not isinstance(url, str) or url == "N/A":
        return False
    # Streamlit natively supports YouTube, Vimeo, and direct links ending in media extensions
    video_patterns = [r'youtube\.com', r'youtu\.be', r'vimeo\.com', r'\.mp4$', r'\.mov$', r'\.webm$']
    return any(re.search(pattern, url.lower()) for pattern in video_patterns)

# --- 2. SIDEBAR & FILTERS ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)
    
    st.divider()
    st.header("📂 WORKOUT HISTORY")
    if st.session_state.archives:
        for a in st.session_state.archives:
            st.write(f"📅 **{a['date']}**")
            st.caption(f"{a['sport']} - {len(a['data'])} Drills")
            st.divider()
    else:
        st.caption("No archived workouts yet.")

    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile"):
        st.session_state.user_profile["name"] = st.text_input("Name", st.session_state.user_profile["name"])
        st.session_state.user_profile["weight"] = st.number_input("Weight", value=st.session_state.user_profile["weight"])

    st.divider()
    st.header("📍 SESSION FILTERS")
    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    location_filter = st.multiselect("Facility Location", ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"], default=["Gym", "Floor"])
    num_drills = st.slider("Target Drills", 5, 20, 10)
    effort = st.select_slider("Effort Level", options=["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": 0.8, "Moderate": 1.0, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. DYNAMIC THEMING ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_blue = "#3B82F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {primary_bg}; color: {text_color}; }}
    div.stButton > button {{
        color: {accent_blue} !important;
        background-color: #FFFFFF !important;
        border: 2px solid {accent_blue} !important;
        font-weight: 800 !important;
        border-radius: 8px;
        width: 100%;
    }}
    .desc-bubble {{ background-color: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid {accent_blue}; margin-bottom: 8px; color: #f8fafc; }}
    .form-bubble {{ background-color: #064e3b; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981; margin-bottom: 12px; color: #ecfdf5; }}
    .metric-label {{ font-size: 0.7rem; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin: 0; }}
    .metric-value {{ font-size: 1rem; color: {accent_blue}; font-weight: 700; margin: 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
def scale_text(val_str, multiplier):
    nums = re.findall(r'\d+', str(val_str))
    new_str = str(val_str)
    for n in nums:
        new_str = new_str.replace(n, str(int(round(int(n) * multiplier))), 1)
    return new_str

@st.cache_data(ttl=3600)
def fetch_data(sport):
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    sport_map = {"Basketball": "basketball.csv", "Softball": "softball.csv", "Track": "track.csv", "Pilates": "pilates.csv", "General": "general.csv"}
    try:
        df = pd.read_csv(f"{base_url}{sport_map[sport]}").fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        return df.to_dict('records')
    except: return []

def build_workout(pool, multiplier, env_selections, limit):
    clean_envs = [s.lower() for s in env_selections]
    filtered = [r for r in pool if str(r.get('Env.', r.get('Location', ''))).lower() in clean_envs or "all" in str(r.get('Env.', '')).lower()]
    
    warmup_pool = [r for r in filtered if "warmup" in str(r.get('type', '')).lower()]
    warmups = random.sample(warmup_pool, min(len(warmup_pool), random.randint(6, 8))) if warmup_pool else []

    mains = [r for r in filtered if "warmup" not in str(r.get('type', '')).lower()]
    types = list(set([str(r.get('type', '')) for r in mains if r.get('type') != 'N/A']))
    chosen_type = random.choice(types) if types else None
    type_matches = [r for r in mains if str(r.get('type', '')) == chosen_type]
    
    candidates = type_matches if len(type_matches) >= 3 else mains
    selected = random.sample(candidates, min(len(candidates), limit))
    
    final_mains = []
    seen = set()
    for d in selected:
        name = str(d.get('Exercise Name', d.get('Exercise', '')))
        if name in seen: continue
        final_mains.append(d)
        seen.add(name)
        
        for p1, p2 in [("left", "right"), ("(l)", "(r)"), ("inside", "outside")]:
            pair_name = None
            if p1 in name.lower(): pair_name = name.lower().replace(p1, p2)
            elif p2 in name.lower(): pair_name = name.lower().replace(p2, p1)
            if pair_name:
                match = next((r for r in mains if str(r.get('Exercise Name', r.get('Exercise', ''))).lower() == pair_name), None)
                if match and str(match.get('Exercise Name', '')) not in seen:
                    final_mains.append(match)
                    seen.add(str(match.get('Exercise Name', '')))

    def scale(d):
        d = d.copy()
        s_val = str(d.get('Sets', '3'))
        d['Sets_S'] = int(round((int(float(s_val)) if s_val.replace('.','').isdigit() else 3) * multiplier))
        d['Reps_S'] = scale_text(d.get('Reps/Dist', d.get('Reps', '10')), multiplier)
        return d

    return [scale(w) for w in warmups], [scale(m) for m in final_mains[:limit]]

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 GENERATE NEW WORKOUT"):
    pool = fetch_data(sport_choice)
    if pool:
        w, m = build_workout(pool, mult, location_filter, num_drills)
        st.session_state.warmup_drills = w
        st.session_state.current_session = m
        st.session_state.set_counts = {i: 0 for i in range(len(m))}
        st.session_state.workout_finished = False
        st.session_state.uploaded_media = {}

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🏆 PRO-ATHLETE TRACKER</h1>", unsafe_allow_html=True)

if st.session_state.current_session and not st.session_state.workout_finished:
    # Warmups
    st.markdown("### 🔥 Suggested Warmups (6-8 Drills)")
    cols = st.columns(2)
    for idx, wd in enumerate(st.session_state.warmup_drills):
        cols[idx % 2].markdown(f"✅ **{wd.get('Exercise Name', 'Drill')}**: {wd['Reps_S']}")
    st.divider()

    # Exercises
    for i, drill in enumerate(st.session_state.current_session):
        with st.expander(f"**{drill.get('Exercise Name', 'Drill')}**", expanded=(i==0)):
            # Bubbles at TOP
            st.markdown(f"<div class='desc-bubble'><b>📝 Description:</b> {drill.get('Description', 'N/A')}</div>", unsafe_allow_html=True)
            if drill.get('Proper Form') != "N/A":
                st.markdown(f"<div class='form-bubble'><b>✨ Proper Form:</b> {drill['Proper Form']}</div>", unsafe_allow_html=True)
            
            # FIXED VIDEO LOGIC
            demo_url = drill.get('Demo', drill.get('Demo_URL', 'N/A'))
            if is_playable_video(demo_url):
                st.video(demo_url)
            elif demo_url != "N/A":
                st.info(f"🔗 [Click here to watch the Demo Video]({demo_url})")
            
            # File Upload
            up = st.file_uploader(f"Upload Clip", key=f"up_{i}")
            if up: st.session_state.uploaded_media[i] = up.name

            # Metadata Row
            cols = st.columns(4)
            exclude = ['Exercise Name', 'Exercise', 'Demo', 'Demo_URL', 'Rank', 'Description', 'Proper Form', 'Sets_S', 'Reps_S', 'Sets', 'Reps', 'Reps/Dist']
            visible = [k for k in drill.keys() if k not in exclude]
            for idx, k in enumerate(visible[:4]):
                cols[idx].markdown(f"<p class='metric-label'>{k}</p><p class='metric-value'>{drill[k]}</p>", unsafe_allow_html=True)
            
            st.markdown(f"**Target:** {drill['Sets_S']} Sets x {drill['Reps_S']}")
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ Log Set ({curr}/{drill['Sets_S']})", key=f"l_{i}"):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
            with c2:
                sw_s, sw_x = st.columns(2)
                if sw_s.button("Start Stopwatch", key=f"ss_{i}"):
                    st.session_state.stopwatch_runs[i] = time.time()
                if sw_x.button("Stop", key=f"sx_{i}"):
                    st.session_state.stopwatch_runs.pop(i, None)
                if i in st.session_state.stopwatch_runs:
                    elapsed = time.time() - st.session_state.stopwatch_runs[i]
                    st.markdown(f"<h2 style='text-align:center; color:{accent_blue};'>{round(elapsed,1)}s</h2>", unsafe_allow_html=True)

    if st.button("🏁 FINISH WORKOUT"):
        st.session_state.workout_finished = True
        st.session_state.archives.append({
            "date": get_now_est().strftime('%Y-%m-%d %H:%M'),
            "sport": sport_choice,
            "data": st.session_state.current_session
        })
        st.rerun()

elif st.session_state.workout_finished:
    st.header("📊 Workout Summary")
    summary_df = pd.DataFrame([{
        "Exercise": d.get('Exercise Name'),
        "Logged": st.session_state.set_counts.get(i, 0),
        "Goal": d['Sets_S'],
        "Media": "Yes" if i in st.session_state.uploaded_media else "No"
    } for i, d in enumerate(st.session_state.current_session)])
    st.table(summary_df)
    
    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Performance CSV", csv, "workout.csv", "text/csv")
    if st.button("New Session"):
        st.session_state.current_session = None
        st.rerun()
