import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz
from collections import defaultdict

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "current_session" not in st.session_state:
    st.session_state.current_session = None

if "archives" not in st.session_state:
    st.session_state.archives = []

if "view_archive_index" not in st.session_state:
    st.session_state.view_archive_index = None

if "set_counts" not in st.session_state:
    st.session_state.set_counts = {}

if "workout_finished" not in st.session_state:
    st.session_state.workout_finished = False

if "timers" not in st.session_state:
    st.session_state.timers = {}

if "stopwatches" not in st.session_state:
    st.session_state.stopwatches = {}

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Elite Athlete",
        "age": 17,
        "weight": 180,
        "goal_weight": 190,
        "hs_goal": "Elite Performance",
        "college_goal": "D1 Scholarship"
    }

# --------------------------------------------------
# TIME
# --------------------------------------------------
def get_now_est():
    return datetime.now(pytz.timezone("US/Eastern"))

# --------------------------------------------------
# LEFT / RIGHT HELPERS
# --------------------------------------------------
def normalize_lr(name):
    n = name.lower()
    if "(l)" in n or "left" in n:
        return re.sub(r"\(l\)|left", "", n).strip(), "L"
    if "(r)" in n or "right" in n:
        return re.sub(r"\(r\)|right", "", n).strip(), "R"
    return n.strip(), None

def pair_left_right(rows):
    grouped = defaultdict(dict)

    for r in rows:
        name = str(r.get("Exercise Name", r.get("Exercise", "")))
        base, side = normalize_lr(name)

        if side:
            grouped[base][side] = r
        else:
            grouped[base]["single"] = r

    ordered = []
    for base in grouped:
        if "L" in grouped[base]:
            ordered.append(grouped[base]["L"])
        if "R" in grouped[base]:
            ordered.append(grouped[base]["R"])
        if "single" in grouped[base]:
            ordered.append(grouped[base]["single"])

    return ordered

# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------
def scale_text(val, mult):
    nums = re.findall(r"\d+", str(val))
    out = str(val)
    for n in nums:
        out = out.replace(n, str(int(round(int(n) * mult))), 1)
    return out

def extract_url(text):
    if not isinstance(text, str):
        return ""
    m = re.search(r"(https?://[^\s]+)", text)
    return m.group(1) if m else ""

def get_csv_urls(sport, envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {
        "Basketball": f"{base}basketball.csv",
        "Softball": f"{base}softball.csv",
        "Track": f"{base}track.csv",
        "Pilates": f"{base}pilates.csv",
        "General": f"{base}general.csv",
    }

    files = [urls.get(sport, urls["General"])]

    files += [
        f"{base}general-loop-band.csv",
        f"{base}general-mini-bands.csv",
    ]

    if "Weight Room" in envs:
        files += [
            f"{base}barbell.csv",
            f"{base}general-dumbell.csv",
            f"{base}general-kettlebell.csv",
            f"{base}general-medball.csv",
        ]

    return files

def load_workout(sport, mult, envs, limit):
    rows = []

    for url in get_csv_urls(sport, envs):
        try:
            df = pd.read_csv(url).fillna("N/A")
            df.columns = [c.strip() for c in df.columns]
            rows.extend(df.to_dict("records"))
        except:
            continue

    random.shuffle(rows)
    rows = rows[:limit]
    rows = pair_left_right(rows)

    workout = []
    for r in rows:
        workout.append({
            "raw": r,
            "sets": int(round(float(r.get("Sets", 3)) * mult)),
            "reps": scale_text(r.get("Reps", r.get("Reps/Dist", "10")), mult),
            "demo": extract_url(r.get("Demo", ""))
        })

    return workout

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("🎨 Appearance")
    dark_mode = st.toggle("Dark Mode", True)

    st.divider()
    st.header("👤 Athlete Profile")
    p = st.session_state.user_profile
    p["name"] = st.text_input("Name", p["name"])
    p["age"] = st.number_input("Age", 10, 60, p["age"])
    p["weight"] = st.number_input("Weight", value=p["weight"])
    p["goal_weight"] = st.number_input("Goal Weight", value=p["goal_weight"])
    p["hs_goal"] = st.text_input("HS Goal", p["hs_goal"])
    p["college_goal"] = st.text_input("College Goal", p["college_goal"])

    st.divider()
    st.header("📍 Filters")
    sport = st.selectbox("Sport", ["Basketball", "Softball", "Track", "Pilates", "General"])
    envs = st.multiselect("Environment", ["Gym", "Field", "Weight Room", "Track", "Floor"], ["Gym"])
    drills = st.slider("Number of Drills", 5, 25, 12)

    effort = st.select_slider("Effort", ["Low", "Moderate", "High", "Elite"], value="Moderate")
    mult = {"Low": .8, "Moderate": 1, "High": 1.2, "Elite": 1.4}[effort]

    if st.button("🚀 Generate Workout", use_container_width=True):
        st.session_state.current_session = load_workout(sport, mult, envs, drills)
        st.session_state.set_counts = {}
        st.session_state.workout_finished = False
        st.rerun()

# --------------------------------------------------
# THEME
# --------------------------------------------------
bg = "#0F172A" if dark_mode else "#FFFFFF"
fg = "#F8FAFC" if dark_mode else "#0F172A"

st.markdown(
    f"<style>.stApp{{background:{bg};color:{fg};}}</style>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# MAIN UI
# --------------------------------------------------
st.title("🏆 Pro-Athlete Performance")

if st.session_state.current_session and not st.session_state.workout_finished:

    for i, d in enumerate(st.session_state.current_session):
        raw = d["raw"]
        name = raw.get("Exercise Name", "Exercise")

        with st.expander(f"{i+1}. {name}", expanded=i == 0):

            cols = st.columns(3)
            idx = 0
            for k, v in raw.items():
                cols[idx].markdown(f"**{k}:** {v}")
                idx = (idx + 1) % 3

            st.markdown(f"**Sets:** {d['sets']} | **Reps:** {d['reps']}")

            if d["demo"]:
                st.video(d["demo"])

            c1, c2 = st.columns(2)

            with c1:
                done = st.session_state.set_counts.get(i, 0)
                if st.button(f"Log Set {done}/{d['sets']}", key=f"s{i}"):
                    st.session_state.set_counts[i] = min(done + 1, d["sets"])
                    st.rerun()

            with c2:
                if st.button("⏱ Start Stopwatch", key=f"sw{i}"):
                    st.session_state.stopwatches[i] = time.time()
                    st.rerun()

                if i in st.session_state.stopwatches:
                    st.markdown(
                        f"**Elapsed:** {round(time.time() - st.session_state.stopwatches[i],1)}s"
                    )

    if st.button("🏁 Finish Workout", use_container_width=True):
        st.session_state.archives.append({
            "date": get_now_est().strftime("%Y-%m-%d %H:%M"),
            "sport": sport,
            "data": st.session_state.current_session
        })
        st.session_state.workout_finished = True
        st.rerun()

elif st.session_state.workout_finished:
    st.success("Workout Complete 🎉")
    if st.button("Start New Workout"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()

else:
    st.info("Use the sidebar to generate a workout.")
