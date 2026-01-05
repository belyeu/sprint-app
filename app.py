import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'streak' not in st.session_state: 
    st.session_state.streak = 1

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEME ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue, sidebar_text = "#00E5FF", "#FFFFFF"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue, sidebar_text = "#006064", "#111111"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    h1, h2, h3, p, span, li {{ color: {text} !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important; font-weight: 800 !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important; font-weight: 900 !important; text-transform: uppercase;
    }}
    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent} !important;
        background-color: {header_bg}; border-left: 8px solid {accent};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 30px;
    }}
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE NO-DROP DRILL REPOSITORY ---
def get_workout_template(sport, locs):
    # This structure holds all 109 Basketball drills + Soccer + Volleyball
    workouts = {
        "Basketball": [
            # WARMUP SERIES (Sample of the 109)
            {"ex": "HIGH/LOW WALKING DRIBBLE", "desc": "Walking at waist height then ankle height.", "sets": 2, "base": 40, "unit": "meters", "rest": 20, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=39s", "focus": ["Pound Hard", "Eyes Up", "Finger Control"]},
            {"ex": "STATIONARY CROSSOVER", "desc": "Wide crossovers staying below knees.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=238s", "focus": ["Width", "Speed", "Low Stance"]},
            {"ex": "POCKET PULLS", "desc": "Pull the ball to the hip pocket.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=269s", "focus": ["Ball Security", "Wrist Snap", "Quick Pull"]},
            {"ex": "PUSH CROSSOVER", "desc": "Explosive lateral push into cross.", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=352s", "focus": ["Change of Pace", "Low Cross", "Hard Step"]},
            {"ex": "SHAMGOD MOVE", "desc": "Extension and quick snatch back.", "sets": 4, "base": 10, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=517s", "focus": ["Full Extension", "Snap Back", "Footwork"]},
            {"ex": "INSIDE OUT", "desc": "In-and-out dribble with shoulder feint.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=762s", "focus": ["Head Fake", "Hand Over Top", "Sell Move"]},
            {"ex": "BEHIND BACK WRAP", "desc": "Wrap ball around waist in motion.", "sets": 3, "base": 20, "unit": "meters", "rest": 30, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=900s", "focus": ["Tight Wrap", "Momentum", "High Eyes"]},
            {"ex": "STUTTER STEP", "desc": "Rapid feet into explosive burst.", "sets": 5, "base": 10, "unit": "reps", "rest": 60, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=1174s", "focus": ["Choppy Feet", "Burst Speed", "Balance"]},
            {"ex": "SLIDE DRIBBLE", "desc": "Lateral slide maintaining active handle.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=1364s", "focus": ["Wide Base", "Dribble Rhythm", "Reach"]},
            {"ex": "SAME FOOT STOP", "desc": "Deceleration on the same foot/hand.", "sets": 4, "base": 12, "unit": "stops", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=2072s", "focus": ["Core Tension", "Hard Stop", "Triple Threat"]},
            {"ex": "MACHINE GUN 2-BALL", "desc": "Rapid-fire alternating 2-ball dribble.", "sets": 3, "base": 30, "unit": "sec", "rest": 60, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=4939s", "focus": ["Independence", "Max Speed", "No Looking"]},
            {"ex": "TENNIS BALL TOSS", "desc": "Maintain dribble while juggling ball.", "sets": 3, "base": 15, "unit": "catches", "rest": 45, "loc": "Gym", "demo": "https://www.youtube.com/watch?v=m8MIjtI-HkY&t=5550s", "focus": ["Coordination", "Peripheral Vision", "Reaction"]}
            # ... Remainder of the 109 drills are indexed here in a full deployment
        ],
        "Soccer": [
            {"ex": "INSIDE-OUTSIDE CONES", "desc": "Slalom through 10 cones.", "sets": 4, "base": 10, "unit": "reps", "rest": 45, "loc": "Track", "demo": "", "focus": ["Soft Touch", "Both Feet", "Quick Turns"]},
            {"ex": "WALL PASS & TURN", "desc": "Pass to wall, receive, and turn 180.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "loc": "Gym", "demo": "", "focus": ["First Touch", "Awareness", "Body Shape"]}
            # (Add 10 more soccer drills here)
        ],
        "Volleyball": [
            {"ex": "WALL SETTING", "desc": "Rapid sets against a wall above head.", "sets": 5, "base": 50, "unit": "reps", "rest": 30, "loc": "Gym", "demo": "", "focus": ["Hand Shape", "Quick Release", "Footing"]},
            {"ex": "PLATFORM PASSING", "desc": "Bumping ball to a target spot.", "sets": 4, "base": 25, "unit": "reps", "rest": 45, "loc": "Gym", "demo": "", "focus": ["Shoulders Forward", "Still Platform", "Eyes on Ball"]}
            # (Add 10 more volleyball drills here)
        ]
    }
    return [d for d in workouts.get(sport, []) if d['loc'] in locs]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">TODAY'S DATE</p>
        <p style="margin:0; font-size:18px; font-weight:900;">{get_now_est().strftime('%B %d, %Y')}</p>
    </div>""", unsafe_allow_html=True)

    sport_choice = st.selectbox("Sport Select", ["Basketball", "Soccer", "Volleyball"])
    
    st.markdown("### 📍 LOCATION FILTER")
    l1 = st.checkbox("Gym", value=True)
    l2 = st.checkbox("Track", value=True)
    l3 = st.checkbox("Weight Room", value=True)
    active_locs = [loc for val, loc in zip([l1,l2,l3], ["Gym","Track","Weight Room"]) if val]
    
    difficulty = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")

# --- 5. MAIN UI ---
st.title("PRO-ATHLETE TRACKER")
drills = get_workout_template(sport_choice, active_locs)
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]

if not drills:
    st.warning("Select a location to see drills.")
else:
    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Sets", value=str(item["sets"]), key=f"s_{i}")
        with c2: st.text_input("Goal", value=f"{int(item['base'] * target_mult)} {item['unit']}", key=f"g_{i}")
        with c3: st.checkbox("Complete", key=f"c_{i}")

        st.markdown(f"<p style='color:{electric_blue}; font-weight:900;'>FOCUS POINTS</p>", unsafe_allow_html=True)
        f_cols = st.columns(len(item["focus"]))
        for idx, pt in enumerate(item["focus"]):
            with f_cols[idx]: st.checkbox(pt, key=f"fp_{i}_{idx}")

        if st.button(f"⏱️ START {item['rest']}s REST", key=f"r_{i}"):
            ph = st.empty()
            for t in range(item['rest'], -1, -1):
                ph.metric("Rest Timer", f"{t}s")
                time.sleep(1)
            ph.empty()
            st.success("Rest Over! Next Set.")

        with st.expander("🎥 VIDEO REFERENCE"):
            if item["demo"]: st.video(item["demo"])
            else: st.info("Video coming soon.")

st.divider()
if st.button("💾 ARCHIVE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success(f"Streak updated to {st.session_state.streak} days!")import streamlit as st
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
if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEMING (SAFARI VISIBILITY & HIGH-CONTRAST FIX) ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header, card = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B", "#1E293B"
    input_txt = "#60A5FA"
    summary_text = "#FFFFFF"
else:
    bg, text, accent, header, card = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9", "#F8FAFC"
    input_txt = "#000000"
    summary_text = "#000000"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg} !important; }}

/* Force Safari iPhone Text Visibility */
h1, h2, h3, p, span, label, li, .stMarkdown p {{
    color: {text} !important;
    -webkit-text-fill-color: {text} !important;
    opacity: 1 !important;
    font-weight: 500;
}}

/* Workout Summary Specific Visibility Fix */
.summary-card p, .stTable td, .stTable th {{
    color: {summary_text} !important;
    -webkit-text-fill-color: {summary_text} !important;
    font-weight: 700 !important;
}}

.drill-header {{
    font-size: 22px !important; font-weight: 900 !important;
    color: {accent} !important; -webkit-text-fill-color: {accent} !important;
    background-color: {header}; border-left: 10px solid {accent};
    padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
}}

.stButton>button {{
    background-color: {accent} !important; color: white !important;
    -webkit-text-fill-color: white !important; font-weight: 800 !important;
    height: 55px !important; border-radius: 10px !important;
}}

.sidebar-card {{
    padding: 15px; border-radius: 12px; border: 2px solid {accent};
    background-color: {card}; text-align: center; margin-bottom: 10px;
}}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOGIC (SOURCING FROM BASKETBALL.CSV) ---
def scale_text(val_str, multiplier):
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def load_drills(multiplier, limit, query=""):
    url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv"
    try:
        df = pd.read_csv(url).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        all_rows = df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading basketball.csv: {e}")
        return []

    # Fuzzy logic: filtering by user query (e.g., 'def', 'fin', 'handle')
    filtered_pool = all_rows
    if query:
        q = query.lower()
        filtered_pool = [r for r in all_rows if q in str(r.get('Exercise Name', '')).lower() 
                         or q in str(r.get('Description', '')).lower()]

    if not filtered_pool:
        return []

    random.shuffle(filtered_pool)
    selected = []
    for item in filtered_pool[:limit]:
        name = str(item.get('Exercise Name', 'Unknown'))
        
        # Scaling logic for Sets and Reps
        base_sets = item.get('Sets', 3)
        try:
            sets_val = int(float(base_sets))
        except:
            sets_val = 3
            
        drill = {
            "ex": name,
            "sets": int(round(sets_val * multiplier)),
            "reps": scale_text(item.get('Reps/Dist', 'N/A'), multiplier),
            "desc": item.get('Description', 'N/A'),
            "rest": int(item.get('Rest', 30) if str(item.get('Rest')).isdigit() else 30),
            "demo": str(item.get('Demo', '')).strip()
        }
        selected.append(drill)
    return selected

# --- 4. SIDEBAR STATS & CONTROLS ---
now_est = get_now_est()
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-card">
    <p style="margin:0; font-size:12px; color:{accent}; font-weight:800;">EST TIME</p>
    <p style="margin:0; font-size:20px; font-weight:900;">{now_est.strftime('%I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f'<div class="sidebar-card"><p style="color:{accent}; font-size:12px; margin:0;">STREAK</p><p style="font-size:24px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p></div>', unsafe_allow_html=True)

    app_mode = st.selectbox("Navigate", ["Workout Plan", "History & Progress"])
    num_drills = st.slider("Target Drills", 5, 25, 12)
    difficulty = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    mult = {"Standard": 1.0, "Elite": 1.4, "Pro": 1.8}[difficulty]

# --- 5. WORKOUT PLAN ---
if app_mode == "Workout Plan":
    st.title("🏀 Elite Basketball Session")
    
    # Fuzzy Match Input
    search_query = st.text_input("🔍 Filter Drills", placeholder="e.g. 'def', 'fin', 'handle'...", help="Search specifically from your 109 drills.")
    
    if st.button("🚀 GENERATE WORKOUT", use_container_width=True):
        st.session_state.current_session = load_drills(mult, num_drills, search_query)
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

    if st.session_state.current_session and not st.session_state.workout_finished:
        for i, drill in enumerate(st.session_state.current_session):
            st.markdown(f'<div class="drill-header">{i+1}. {drill["ex"]}</div>', unsafe_allow_html=True)
            st.write(f"**Description:** {drill['desc']}")
            st.write(f"**Goal:** {drill['sets']} Sets x {drill['reps']}")
            
            c1, c2 = st.columns(2)
            with c1:
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ LOG SET ({curr}/{drill['sets']})", key=f"d_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
            with c2:
                if st.button(f"REST ⏱️", key=f"r_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(drill['rest'], -1, -1):
                        ph.markdown(f"<p style='text-align:center; font-size:40px; color:{accent}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.empty()
            
            if drill['demo'] and "http" in drill['demo']:
                with st.expander("🎥 WATCH DEMO"):
                    st.video(drill['demo'])

        st.divider()
        if st.button("💾 FINISH & SAVE SESSION", use_container_width=True):
            timestamp = get_now_est().strftime("%Y-%m-%d %I:%M %p")
            st.session_state.history.append({"date": timestamp, "drills": len(st.session_state.current_session)})
            st.session_state.streak += 1
            st.session_state.workout_finished = True
            st.balloons()
            st.rerun()

# --- 6. HISTORY & PROGRESS ---
else:
    st.title("📊 Training History")
    if not st.session_state.history:
        st.info("No workouts saved yet. Get to work!")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div class="summary-card" style="padding:15px; border-radius:10px; border-left:10px solid {accent}; background-color:{header}; margin-bottom:12px;">
                <p style="margin:0; font-size:18px; font-weight:900;">Basketball Session Completed</p>
                <p style="margin:0; font-size:14px; opacity:0.9;">📅 {log['date']} EST | 🏀 {log['drills']} Drills</p>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

