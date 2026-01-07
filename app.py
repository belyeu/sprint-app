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
if 'warmup_drills' not in st.session_state:
    st.session_state.warmup_drills = None
if 'stopwatch_runs' not in st.session_state:
    st.session_state.stopwatch_runs = {}

if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
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

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", True)

    st.divider()
    st.header("👤 ATHLETE PROFILE")
    with st.expander("Edit Profile & Goals"):
        p = st.session_state.user_profile
        p["name"] = st.text_input("Name", p["name"])
        c1, c2 = st.columns(2)
        p["age"] = c1.number_input("Age", 10, 50, p["age"])
        p["weight"] = c2.number_input("Weight (lbs)", value=p["weight"])
        p["goal_weight"] = st.number_input("Goal Weight (lbs)", value=p["goal_weight"])
        p["hs_goal"] = st.text_input("HS Goal", p["hs_goal"])
        p["college_goal"] = st.text_input("College Goal", p["college_goal"])

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
    effort = st.select_slider("Effort Level", ["Low", "Moderate", "High", "Elite"], "Moderate")
    mult = {"Low": .8, "Moderate": 1, "High": 1.2, "Elite": 1.4}[effort]

# --- 3. THEME (UNCHANGED) ---
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent_color = "#3B82F6"

st.markdown(f"""
<style>
.stApp {{ background:{primary_bg}; color:{text_color}; }}
div[data-testid="stExpander"] details summary {{
    background:{accent_color}; color:white; border-radius:8px; padding:.6rem 1rem;
}}
</style>
""", unsafe_allow_html=True)

# --- 4. DATA HELPERS ---
def scale_text(val, mult):
    out = str(val)
    for n in re.findall(r'\d+', out):
        out = out.replace(n, str(int(round(int(n) * mult))), 1)
    return out

def normalize_lr(name):
    n = name.lower()
    if "(l)" in n or "left" in n:
        return re.sub(r'\(l\)|left', '', n).strip(), "L"
    if "(r)" in n or "right" in n:
        return re.sub(r'\(r\)|right', '', n).strip(), "R"
    return n.strip(), None

def get_csv_url(sport):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    return f"{base}{sport.lower()}.csv" if sport != "General" else f"{base}general.csv"

# --- 5. LOAD + BUILD WORKOUT ---
def load_and_build_workout(sport, mult, envs, limit, intensity):
    try:
        df = pd.read_csv(get_csv_url(sport)).fillna("N/A")
        df.columns = [c.strip() for c in df.columns]
        rows = df.to_dict("records")
    except:
        return [], []

    envs = [e.lower() for e in envs]
    pool = [r for r in rows if str(r.get("Env.", "")).lower() in envs or "all" in str(r.get("Env.", "")).lower()]

    warmups = [r for r in pool if "warmup" in str(r.get("Type", "")).lower()]
    warmups = random.sample(warmups, min(len(warmups), random.randint(6, 10)))

    mains = [r for r in pool if r not in warmups]
    random.shuffle(mains)

    paired = []
    seen = set()

    for r in mains:
        name = str(r.get("Exercise Name", r.get("Exercise", "")))
        base, side = normalize_lr(name)

        if name in seen:
            continue

        paired.append(r)
        seen.add(name)

        if side == "L":
            target = re.sub(r'\(l\)|left', '(R)', name, flags=re.I)
            pair = next((x for x in mains if str(x.get("Exercise Name", "")) == target), None)
            if pair:
                paired.append(pair)
                seen.add(target)

        if len(paired) >= limit:
            break

    for d in warmups + paired:
        d["Sets_Scaled"] = int(round(float(d.get("Sets", 3)) * mult))
        d["Reps_Scaled"] = scale_text(d.get("Reps/Dist", d.get("Reps", "10")), mult)

    return warmups, paired

# --- 6. EXECUTION ---
if st.sidebar.button("🚀 GENERATE
