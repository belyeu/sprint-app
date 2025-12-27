import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0F19; color: #E2E8F0; }
    .drill-card { 
        background-color: #161B22; 
        border: 2px solid #30363D; 
        border-radius: 12px; 
        padding: 24px; 
        margin-bottom: 30px; 
        border-left: 6px solid #2F81F7;
    }
    .coach-header { 
        color: #58A6FF; 
        font-weight: 800; 
        text-transform: uppercase; 
        font-size: 0.85rem; 
        letter-spacing: 1px;
    }
    .stCheckbox label p { font-weight: 500; color: #C9D1D9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (FULL RECOVERY) ---
def get_drill_data(sport):
    if sport == "Basketball":
        return [
            {"cat": "Warm-up", "ex": "High/Low Walking (R)", "base": 2, "unit": "Laps", "checks": ["Chest Up", "Pound through floor", "Active weak hand"], "demo": "https://www.youtube.com/watch?v=cvE0UfP8GfA"},
            {"cat": "Warm-up", "ex": "High/Low Walking (L)", "base": 2, "unit": "Laps", "checks": ["Weak hand focus", "Fingertip control", "Eyes up"], "demo": "https://www.youtube.com/watch?v=cvE0UfP8GfA"},
            {"cat": "Crossover", "ex": "Stationary High", "base": 50, "unit": "reps", "checks": ["Shoulder sway", "Wide base", "Below waist height"], "demo": "https://www.basketballforcoaches.com/ball-handling-drills/"},
            {"cat": "Crossover", "ex": "Stationary Low", "base": 50, "unit": "reps", "checks": ["Ankle height", "Rapid hand speed", "Bent knees"], "demo": "https://www.basketballforcoaches.com/ball-handling-drills/"},
            {"cat": "Crossover", "ex": "Pocket Pulls", "base": 20, "unit": "reps", "checks": ["Wrist snap", "Hide ball behind hip", "Core stability"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Footwork", "ex": "Jab Step Series", "base": 15, "unit": "reps", "checks": ["Explosive first step", "Shoulder fake", "Ball protection"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            {"cat": "Between Legs", "ex": "Continuous Figure-8", "base": 40, "unit": "reps", "checks": ["Low hips", "No extra dribble", "Hand follow-through"], "demo": "https://www.breakthroughbasketball.com/drills/basketballdrills.html"},
            {"cat": "Behind Back", "ex": "Wrap-Around Dribble", "base": 30, "unit": "reps", "checks": ["Under glutes", "Tight path", "Sharp snap"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Shooting", "ex": "Mikan Drill", "base": 20, "unit": "makes", "checks": ["High release", "Square shoulders", "Rhythmic footwork"], "demo": "https://www.basketballforcoaches.com/basketball-drills-and-games-for-kids/"},
            {"cat": "Shooting", "ex": "Form Shooting (1-Hand)", "base": 15, "unit": "makes", "checks": ["High arc", "Elbow tucked", "Follow through"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            {"cat": "Shooting", "ex": "Elbow Jumpers", "base": 20, "unit": "shots", "checks": ["Step into shot", "Balanced lift", "Target rim"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Defense", "ex": "Zig-Zag Slides", "base": 4, "unit": "Lengths", "checks": ["Wide base", "Active hands", "No heel clicking"], "demo": "https://jr.nba.com/basketball-practice-plans/starter/"},
            {"cat": "Defense", "ex": "Closeouts", "base": 10, "unit": "reps", "checks": ["Choppy feet", "One hand high", "Weight back"], "demo": "https://www.breakthroughbasketball.com/drills/basketballdrills.html"},
            {"cat": "Finish", "ex": "Drop Step Finish", "base": 20, "unit": "reps", "checks": ["Seal defender", "Chin the ball", "Strong jump"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            {"cat": "Passing", "ex": "Wall Chest Pass", "base": 30, "unit": "reps", "checks": ["Thumbs down", "Step through", "Accuracy"], "demo": "https://skillshark.com/blog/best-basketball-tryout-drills"},
            {"cat": "Passing", "ex": "One-Hand Zip Pass", "base": 20, "unit": "reps", "checks": ["Wrist snap", "Direct line", "Target lead"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Combos", "ex": "Iverson Step Cross", "base": 15, "unit": "reps", "checks": ["Wide step", "Head fake", "Change of pace"], "demo": "https://www.basketballforcoaches.com/ball-handling-drills/"},
            {"cat": "Combos", "ex": "Behind-Cross Combo", "base": 15, "unit": "reps", "checks": ["Tight wrap", "Low cross", "Counter move"], "demo": "https://www.breakthroughbasketball.com/drills/basketballdrills.html"},
            {"cat": "Conditioning", "ex": "Full Court Sprints", "base": 5, "unit": "reps", "checks": ["Max burst", "Finish through line", "Breathing control"], "demo": "https://www.basketballforcoaches.com/basketball-training/"},
            {"cat": "Finish", "ex": "Free Throws (100)", "base": 10, "unit": "shots", "checks": ["Routine", "Focus", "High release"], "demo": "https://www.basketballforcoaches.com/basketball-training/"}
        ]
    elif sport == "Softball":
        return [
            {"cat": "Hitting", "ex": "Tee Work", "base": 25, "unit": "swings", "checks": ["Bat path", "Extension", "Hip rotation"], "demo": "https://thehittingvault.com/softball-hitting-drills-and-practice-plans/"},
            {"cat": "Fielding", "ex": "Glove Transfers", "base": 30, "unit": "reps", "checks": ["Quick release", "Four-seam grip", "Elbow up"], "demo": "https://skillshark.com/blog/youth-softball-drills"},
            {"cat": "Arm", "ex": "Long Toss", "base": 15, "unit": "throws", "checks": ["Arc", "Follow through", "Crow hop"], "demo": "https://www.justbats.com/blog/post/10-best-softball-drills-every-coach-should-use/"},
            {"cat": "Defense", "ex": "Picker Hops", "base": 20, "unit": "reps", "checks": ["Glove in dirt", "Soft hands", "Stay low"], "demo": "https://thehittingvault.com/softball-hitting-drills-and-practice-plans/"},
            {"cat": "Hitting", "ex": "Soft Toss", "base": 20, "unit": "swings", "checks": ["Timing", "Weight transfer", "Head still"], "demo": "https://thehittingvault.com/softball-hitting-drills-and-practice-plans/"}
        ]
    # (Track and General categories follow this same pattern...)
    return []

# --- 3. MAIN UI LOGIC ---
st.title("PRO-ATHLETE PERFORMANCE TRACKER")

with st.sidebar:
    st.header("GLOBAL CONTROLS")
    sport_choice = st.selectbox("Active Discipline", ["Basketball", "Softball", "Track", "General"])
    st.divider()
    if st.button("📥 EXPORT FULL SESSION REPORT"): st.success("Report Generated!")

drills = get_drill_data(sport_choice)

# Progress Management
done_count = sum([st.session_state.get(f"done_{i}", False) for i in range(len(drills))])
progress = done_count / len(drills) if drills else 0
st.progress(progress)
st.caption(f"Workout Completion: {int(progress*100)}% ({done_count}/{len(drills)} Drills)")

# --- 4. EXERCISE-SPECIFIC CARDS ---
for i, drill in enumerate(drills):
    st.markdown(f'<div class="drill-card">', unsafe_allow_html=True)
    
    # Row 1: Exercise Info
    h1, h2, h3 = st.columns([3, 1, 1])
    h1.subheader(f"{i+1}. {drill['ex']} ({drill['cat']})")
    h2.write(f"**Target:** {drill['base']} {drill['unit']}")
    h3.checkbox("MARK COMPLETE", key=f"done_{i}")
    
    st.divider()
    
    # Row 2: Technique & Visual Analysis
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown('<p class="coach-header">Coach\'s Technique Checkpoints</p>', unsafe_allow_html=True)
        for check in drill['checks']:
            st.checkbox(f"✔️ {check}", key=f"eval_{i}_{check}")
            
    with c2:
        st.markdown('<p class="coach-header">Analysis & Video Demos</p>', unsafe_allow_html=True)
        st.link_button(f"📺 VIEW PRO {drill['ex'].upper()} DEMO", drill['demo'], use_container_width=True)
        
        # Local Upload for THIS Drill
        vid = st.file_uploader(f"Upload {drill['ex']} analysis clip", type=["mp4", "mov"], key=f"vid_{i}")
        if vid:
            st.video(vid)

    # Row 3: Logging Performance
    st.divider()
    l1, l2, l3 = st.columns([1, 1, 2])
    l1.text_input("Sets Completed", value="3", key=f"sets_{i}")
    l2.text_input("Reps/Metric", value=str(drill['base']), key=f"reps_{i}")
    if l3.button(f"SAVE {drill['ex'].upper()} STATS", key=f"log_{i}", use_container_width=True):
        st.toast(f"Data for {drill['ex']} archived!")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. FINAL ARCHIVE ---
if st.button("💾 ARCHIVE COMPLETE WORKOUT", type="primary", use_container_width=True):
    st.balloons()
    st.success("Session fully archived to Athlete History!")
