import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# ==================================================
# 1. APP CONFIG & SESSION STATE
# ==================================================
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

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

def get_now_est():
    return datetime.now(pytz.timezone("US/Eastern"))

# ==================================================
# 2. SIDEBAR
# ==================================================
with st.sidebar:
    st.header("🎨 APPEARANCE")
    dark_mode = st.toggle("Enable Dark Mode", value=True)

    st.divider()
    st.header("📂 WORKOUT HISTORY")

    if st.session_state.archives:
        names = [f"{a['date']} - {a['sport']}" for a in st.session_state.archives]
        choice = st.selectbox("View session:", ["Current / New"] + names)

        if choice != "Current / New":
            st.session_state.view_archive_index = names.index(choice)
        else:
            st.session_state.view_archive_index = None
    else:
        st.caption("No archived workouts yet")

    st.divider()
    st.header("👤 ATHLETE PROFILE")

    with st.expander("Edit Profile"):
        p = st.session_state.user_profile
        p["name"] = st.text_input("Name", p["name"])
        c1, c2 = st.columns(2)
        p["age"] = c1.number_input("Age", 10, 50, p["age"])
        p["weight"] = c2.number_input("Weight", value=p["weight"])
        p["goal_weight"] = st.number_input("Goal Weight", value=p["goal_weight"])
        p["hs_goal"] = st.text_input("HS Goal", p["hs_goal"])
        p["college_goal"] = st.text_input("College Goal", p["college_goal"])

    st.divider()
    st.header("📍 SESSION FILTERS")

    sport_choice = st.selectbox(
        "Sport",
        ["Basketball", "Softball", "Track", "Pilates", "General"]
    )

    location_filter = st.multiselect(
        "Environment",
        ["Gym", "Field", "Cages", "Weight Room", "Track", "Outdoor", "Floor", "General"],
        default=["Gym", "Floor"]
    )

    num_drills = st.slider("Target Drills", 5, 20, 13)

    st.divider()
    st.header("📊 INTENSITY")

    effort = st.select_slider(
        "Effort Level",
        ["Low", "Moderate", "High", "Elite"],
        value="Moderate"
    )

    mult = {
        "Low": 0.8,
        "Moderate": 1.0,
        "High": 1.2,
        "Elite": 1.4
    }[effort]

    st.markdown(f"**Date:** {get_now_est().strftime('%Y-%m-%d')}")

# ==================================================
# 3. STYLING
# ==================================================
primary_bg = "#0F172A" if dark_mode else "#FFFFFF"
card_bg = "#1E293B" if dark_mode else "#F8FAFC"
text_color = "#F8FAFC" if dark_mode else "#1E293B"
accent = "#3B82F6"

st.markdown(f"""
<style>
.stApp {{
    background-color: {primary_bg};
    color: {text_color};
}}

.stButton button {{
    color: black !important;
    font-weight: 700 !important;
}}

div[data-testid="stExpander"] summary {{
    background-color: {accent};
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: 600;
}}

.metric-label {{
    font-size: 0.75rem;
    color: #94A3B8;
    font-weight: bold;
    text-transform: uppercase;
}}

.metric-value {{
    font-size: 1.1rem;
    color: {accent};
    font-weight: 700;
}}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 4. DATA HELPERS
# ==================================================
@st.cache_data(ttl=3600)
def load_csv(url):
    return pd.read_csv(url).fillna("N/A")

def safe_int(val, default=3):
    try:
        return int(float(val))
    except:
        return default

def scale_text(text, mult):
    nums = re.findall(r"\d+", str(text))
    out = str(text)
    for n in nums:
        out = out.replace(n, str(int(round(int(n) * mult))), 1)
    return out

def extract_url(val):
    if not isinstance(val, str):
        return ""
    m = re.search(r"(https?://[^\s]+)", val)
    return m.group(1) if m else ""

def csv_urls(sport, envs):
    base = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    urls = {
        "Basketball": "basketball.csv",
        "Softball": "softball.csv",
        "Track": "track.csv",
        "Pilates": "pilates.csv",
        "General": "general.csv"
    }
    files = [base + urls.get(sport, "general.csv")]
    files += [base + "general-loop-band.csv", base + "general-mini-bands.csv"]

    if "Weight Room" in envs:
        files += [
            base + "barbell.csv",
            base + "general-dumbell.csv",
            base + "general-kettlebell.csv",
            base + "general-medball.csv",
            base + "general-cable-crossover.csv"
        ]
    return files

def build_workout(sport, mult, envs, limit):
    rows = []
    for url in csv_urls(sport, envs):
        try:
            df = load_csv(url)
            rows.extend(df.to_dict("records"))
        except:
            pass

    clean_envs = [e.lower() for e in envs]
    pool = []

    for r in rows:
        loc = str(r.get("Env.", r.get("Location", "General"))).lower()
        if loc in clean_envs or "all" in loc:
            pool.append(r)

    random.shuffle(pool)
    selected = []
    seen = set()

    for r in pool:
        if len(selected) >= limit:
            break

        name = r.get("Exercise Name", r.get("Exercise", "Unknown"))
        if name in seen:
            continue

        seen.add(name)
        sets = safe_int(r.get("Sets", 3))

        drill = {
            "ex": name,
            "env": r.get("Env.", "General"),
            "category": r.get("Category", "Skill"),
            "cns": r.get("CNS", "Low"),
            "focus": r.get("Primary Focus", "Performance"),
            "stars": r.get("Stars", "⭐⭐⭐"),
            "pre_req": r.get("Pre-Req", "N/A"),
            "sets": int(round(sets * mult)),
            "reps": scale_text(r.get("Reps/Dist", "10"), mult),
            "time": r.get("Time", "N/A"),
            "desc": r.get("Description", "See demo."),
            "proper_form": r.get("Proper Form", "Maintain control."),
            "demo": extract_url(r.get("Demo", ""))
        }

        selected.append(drill)

    return selected

# ==================================================
# 5. GENERATE WORKOUT
# ==================================================
if st.sidebar.button("🚀 GENERATE NEW WORKOUT", use_container_width=True):
    workout = build_workout(sport_choice, mult, location_filter, num_drills)
    if workout:
        st.session_state.current_session = workout
        st.session_state.set_counts = {i: 0 for i in range(len(workout))}
        st.session_state.workout_finished = False
        st.session_state.view_archive_index = None
        st.rerun()
    else:
        st.error("No drills found.")

# ==================================================
# 6. MAIN UI
# ==================================================
st.markdown("<h1 style='text-align:center;'>🏆 PRO-ATHLETE PERFORMANCE</h1>", unsafe_allow_html=True)

p = st.session_state.user_profile
st.markdown(
    f"<h3 style='text-align:center;'>Athlete: {p['name']} | Age {p['age']} | {p['weight']} lbs</h3>",
    unsafe_allow_html=True
)

# ---------------- ARCHIVE VIEW ----------------
if st.session_state.view_archive_index is not None:
    arch = st.session_state.archives[st.session_state.view_archive_index]
    st.info(f"📁 Archived Session: {arch['date']} ({arch['sport']})")
    st.table(pd.DataFrame(arch["data"]))

    if st.button("Close Archive"):
        st.session_state.view_archive_index = None
        st.rerun()

# ---------------- ACTIVE WORKOUT ----------------
elif st.session_state.current_session and not st.session_state.workout_finished:

    for i, d in enumerate(st.session_state.current_session):
        with st.expander(f"{i+1}. {d['ex']} {d['stars']}", expanded=i == 0):

            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<p class='metric-label'>Env</p><p class='metric-value'>{d['env']}</p>", unsafe_allow_html=True)
            m2.markdown(f"<p class='metric-label'>Category</p><p class='metric-value'>{d['category']}</p>", unsafe_allow_html=True)
            m3.markdown(f"<p class='metric-label'>CNS</p><p class='metric-value'>{d['cns']}</p>", unsafe_allow_html=True)
            m4.markdown(f"<p class='metric-label'>Focus</p><p class='metric-value'>{d['focus']}</p>", unsafe_allow_html=True)

            st.divider()

            c1, c2 = st.columns(2)

            with c1:
                curr = st.session_state.set_counts[i]
                if st.button(f"Log Set ({curr}/{d['sets']})", key=f"log{i}"):
                    if curr < d["sets"]:
                        st.session_state.set_counts[i] += 1
                        st.rerun()

                if d["demo"]:
                    try:
                        st.video(d["demo"])
                    except:
                        st.markdown(f"[Watch Demo]({d['demo']})")

            with c2:
                tab_timer, tab_sw = st.tabs(["Timer", "Stopwatch"])

                with tab_timer:
                    sec = st.number_input("Seconds", 5, 600, 60, key=f"t{i}")
                    if st.button("Start Timer", key=f"tb{i}"):
                        st.session_state.timers[i] = time.time() + sec
                        st.rerun()

                    if i in st.session_state.timers:
                        rem = int(st.session_state.timers[i] - time.time())
                        if rem <= 0:
                            st.success("Done!")
                            del st.session_state.timers[i]
                        else:
                            st.markdown(f"### {rem}s")
                            time.sleep(0.3)
                            st.rerun()

                with tab_sw:
                    cA, cB = st.columns(2)
                    if cA.button("Start", key=f"swS{i}"):
                        st.session_state.stopwatches[i] = time.time()
                        st.rerun()
                    if cB.button("Stop", key=f"swX{i}"):
                        if i in st.session_state.stopwatches:
                            del st.session_state.stopwatches[i]
                        st.rerun()

                    if i in st.session_state.stopwatches:
                        elapsed = round(time.time() - st.session_state.stopwatches[i], 1)
                        st.markdown(f"### {elapsed}s")
                        time.sleep(0.3)
                        st.rerun()

    if st.button("🏁 FINISH WORKOUT", use_container_width=True):
        summary = [{"Exercise": d["ex"], "Sets": d["sets"], "Reps": d["reps"]} for d in st.session_state.current_session]
        st.session_state.archives.append({
            "date": get_now_est().strftime("%Y-%m-%d %H:%M"),
            "sport": sport_choice,
            "data": summary
        })
        st.session_state.workout_finished = True
        st.rerun()

# ---------------- COMPLETE ----------------
elif st.session_state.workout_finished:
    st.balloons()
    st.success("Workout Complete!")
    st.table(pd.DataFrame([
        {"Exercise": d["ex"], "Sets": d["sets"], "Reps": d["reps"]}
        for d in st.session_state.current_session
    ]))

    if st.button("Start New Session"):
        st.session_state.current_session = None
        st.session_state.workout_finished = False
        st.rerun()

else:
    st.info("👈 Use the sidebar to generate a workout or view history.")
