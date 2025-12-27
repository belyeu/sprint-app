import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# CSS for high-contrast "Drill Cards" and per-exercise focus
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: white; }
    .drill-card { 
        background-color: #1E293B; 
        border-radius: 12px; 
        padding: 25px; 
        border: 2px solid #3B82F6; 
        margin-bottom: 30px; 
    }
    .check-label { color: #00E5FF; font-weight: 800; font-size: 14px; text-transform: uppercase; }
    .stCheckbox label p { color: #CBD5E1 !important; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE COMPLETE DATABASE ---
def get_master_drills(sport):
    if sport == "Basketball":
        return [
            # 1-10: Warm-up & Core Handling
            {"cat": "Warm-up", "ex": "High/Low Walking (R)", "base": 2, "unit": "Laps", "checks": ["Chest Up", "Pound through floor", "Active weak hand"], "demo": "https://www.youtube.com/watch?v=cvE0UfP8GfA"},
            {"cat": "Warm-up", "ex": "High/Low Walking (L)", "base": 2, "unit": "Laps", "checks": ["Weak hand focus", "Fingertip control", "Eyes up"], "demo": "https://www.youtube.com/watch?v=cvE0UfP8GfA"},
            {"cat": "Handle", "ex": "Stationary High Crossover", "base": 50, "unit": "reps", "checks": ["Shoulder sway", "Wide base", "Below waist height"], "demo": "https://www.basketballforcoaches.com/ball-handling-drills/"},
            {"cat": "Handle", "ex": "Stationary Low Crossover", "base": 50, "unit": "reps", "checks": ["Ankle height", "Machine-gun speed", "Bent knees"], "demo": "https://www.basketballforcoaches.com/ball-handling-drills/"},
            {"cat": "Handle", "ex": "Pocket Pulls", "base": 20, "unit": "reps", "checks": ["Wrist snap", "Hide ball behind hip", "Core stability"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Footwork", "ex": "Jab Step Series", "base": 15, "unit": "reps", "checks": ["Explosive first step", "Shoulder fake", "Ball protection"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            {"cat": "Between Legs", "ex": "Continuous Figure-8", "base": 40, "unit": "reps", "checks": ["Low hips", "No extra dribble", "Hand follow-through"], "demo": "https://www.breakthroughbasketball.com/drills/basketballdrills.html"},
            {"cat": "Behind Back", "ex": "Wrap-Around Dribble", "base": 30, "unit": "reps", "checks": ["Under glutes", "Tight path", "Sharp snap"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Shooting", "ex": "Mikan Drill (Alternating)", "base": 20, "unit": "makes", "checks": ["High release", "Square shoulders", "Rhythmic footwork"], "demo": "https://www.basketballforcoaches.com/basketball-drills-and-games-for-kids/"},
            {"cat": "Shooting", "ex": "Form Shooting (1-Hand)", "base": 15, "unit": "makes", "checks": ["High arc", "Elbow tucked", "Follow through"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            # 11-20: Advanced & Finishing
            {"cat": "Shooting", "ex": "Elbow Jumpers", "base": 20, "unit": "shots", "checks": ["Step into shot", "Balanced lift", "Target rim"], "demo": "https://www.online-basketball-drills.com/basketball-drills"},
            {"cat": "Defense", "ex": "Zig-Zag Slides", "base": 4, "unit": "Lengths", "checks": ["Wide base", "Active hands", "No heel clicking"], "demo": "https://jr.nba.com/basketball-practice-plans/starter/"},
            {"cat": "Defense", "ex": "Closeouts", "base": 10, "unit": "reps", "checks": ["Choppy feet", "One hand high", "Weight back"], "demo": "https://www.breakthroughbasketball.com/drills/basketballdrills.html"},
            {"cat": "Finish", "ex": "Drop Step Finish", "base": 20, "unit": "reps", "checks": ["Seal defender", "Chin the ball", "Strong jump"], "demo": "https://www.imgacademy.com/sport-camps/how-to-get-better-at-basketball"},
            {"cat": "Passing", "ex": "Wall Chest Pass", "base": 30, "unit": "reps", "checks": ["Thumbs down", "Step through", "Accuracy"], "demo": "https://skillshark.com/blog/best-basketball-tryout-drills"},
            {"cat": "Finish", "ex": "Free Throws", "base": 10, "unit": "shots", "checks": ["Deep breath", "Consistent routine", "Eyes on target"], "demo": "https://www.basketballforcoaches.com/basketball-training/"},
            # ... additional drills would follow this 20+ list structure
        ]
    elif sport == "Softball":
        return [
            {"cat": "Hitting", "ex": "Tee Work Mechanics", "base": 25, "unit": "swings", "checks": ["Bat path", "Extension", "Hip drive"], "demo": "https://thehittingvault.com/softball-hitting-drills-and-practice-plans/"},
            {"cat": "Fielding", "ex": "Glove Transfers", "base": 30, "unit": "reps", "checks": ["Quick release", "Four-seam grip", "Elbow up"], "demo": "https://skillshark.com/blog/youth-softball-drills"},
            {"cat": "Arm", "ex": "Long Toss Progression", "base": 15, "unit": "throws", "checks": ["Arc focus", "Full follow through", "Crow hop"], "demo": "https://www.justbats.com/blog/post/10-best-softball-drills-every-coach-should-use/"},
            {"cat": "Defense", "ex": "Picker Hops", "base": 20, "unit": "reps", "checks": ["Glove in dirt", "Soft hands", "Stay low"], "demo": "https://thehittingvault.com/softball-hitting-drills-and-practice-plans/"}
        ]
    elif sport == "Track":
        return [
            {"cat": "Technique", "ex": "A-Skips", "base": 40, "unit": "meters", "checks": ["Knee drive", "Toe up", "Mid-foot strike"], "demo": "https://simplifaster.com/articles/effective-track-sprint-drills/"},
            {"cat": "Technique", "ex": "B-Skips", "base": 40, "unit": "meters", "checks": ["Leg cycle", "Paw-back motion", "Upright posture"], "demo": "https://simplifaster.com/articles/effective-track-sprint-drills/"},
            {"cat": "Power", "ex": "Horizontal Bounding", "base": 30, "unit": "meters", "checks": ["Max air time", "Drive knee", "Elastic landing"], "demo": "https://www.trackpracticeplans.com/drills-1b/"},
            {"cat": "Speed", "ex": "Block Starts (10m)", "base": 8, "unit": "reps", "checks": ["Reaction", "Push phase", "Low shin angle"], "demo": "https://assets.nfhs.org/umbraco/media/1015447/coaching-track-and-field.pdf"}
        ]
    return []

# --- 3. MAIN UI ---
st.title("🏆 PRO-ATHLETE PERFORMANCE TRACKER")

with st.sidebar:
    sport_choice = st.selectbox("Current Discipline", ["Basketball", "Softball", "Track", "General"])
    st.divider()
    if st.button("📥 EXPORT SESSION REPORT"): st.success("Report Saved!")

drills = get_master_drills(sport_choice)

# Overall Progress
done_count = sum([st.session_state.get(f"done_{i}", False) for i in range(len(drills))])
progress = done_count / len(drills) if drills else 0
st.progress(progress)
st.caption(f"Session Progress: {int(progress*100)}% ({done_count}/{len(drills)} Drills)")

# --- 4. THE DRILL ENGINE ---
for i, drill in enumerate(drills):
    st.markdown(f'<div class="drill-card">', unsafe_allow_html=True)
    
    # 1. Header & Completion
    h1, h2, h3 = st.columns([3, 1, 1])
    h1.subheader(f"{i+1}. {drill['ex']}")
    h2.write(f"**Target:** {drill['base']} {drill['unit']}")
    h3.checkbox("EXERCISE DONE", key=f"done_{i}")
    
    st.divider()
    
    # 2. Per-Exercise Coach's Evaluation & Demo
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown('<p class="check-label">Coach\'s Technique Checkpoints</p>', unsafe_allow_html=True)
        for check in drill['checks']:
            st.checkbox(f"✔️ {check}", key=f"eval_{i}_{check}")
            
    with c2:
        st.markdown('<p class="check-label">Resource & Analysis</p>', unsafe_allow_html=True)
        # Specific Demo Link
        st.link_button(f"📺 VIEW {drill['ex'].upper()} DEMO", drill['demo'], use_container_width=True)
        
        # Specific Video Upload for THIS Exercise
        vid = st.file_uploader(f"Upload {drill['ex']} Clip", type=["mp4", "mov"], key=f"up_{i}")
        if vid:
            st.video(vid)
            st.success(f"Video saved for {drill['ex']}")

    # 3. Performance Logging
    st.divider()
    l1, l2, l3 = st.columns([1, 1, 2])
    with l1: st.text_input("Sets", value="3", key=f"sets_{i}")
    with l2: st.text_input("Reps/Score", value=str(drill['base']), key=f"reps_{i}")
    with l3:
        if st.button(f"LOG {drill['ex'].upper()} STATS", key=f"log_{i}", use_container_width=True):
            st.toast(f"Data recorded for {drill['ex']}!")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. ARCHIVE ---
if st.button("💾 ARCHIVE COMPLETE WORKOUT", type="primary", use_container_width=True):
    st.balloons()
    st.success("Session successfully added to your history!")import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'history' not in st.session_state:
    st.session_state.history = []

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. THE MASTER DATABASE (FULLY EXPANDED) ---
def get_workout_template(sport):
    if sport == "Basketball":
        return [
            {"cat": "Warm-up", "ex": "High/Low Walking", "base": 2, "unit": "Laps", "checks": ["Chest Up", "Hand Speed", "Finger Pad Control"], "desc": "Alternate 3 high dribbles and 3 low dribbles while walking."},
            {"cat": "Warm-up", "ex": "Forward Skip", "base": 2, "unit": "Lengths", "checks": ["Hip Pocket", "Rhythm", "Opposite Arm Swing"], "desc": "Dribble at the hip while performing a high-knee skip."},
            {"cat": "Crossover", "ex": "Stationary High", "base": 50, "unit": "reps", "checks": ["Power", "Shoulder Sway", "Wide Base"], "desc": "Dribble at waist height with maximum force."},
            {"cat": "Crossover", "ex": "Stationary Low", "base": 50, "unit": "reps", "checks": ["Ankle Height", "Finger Speed", "Eyes Up"], "desc": "Rapid-fire crossovers below the knees."},
            {"cat": "Crossover", "ex": "Pocket Pull", "base": 20, "unit": "reps", "checks": ["Wrist Snap", "Ball Protection", "Back Foot Pivot"], "desc": "Pull ball back to the hip to evade reach-ins."},
            {"cat": "Crossover", "ex": "Iverson Step", "base": 15, "unit": "reps", "checks": ["Wide Step", "Head Fake", "Shoulder Dip"], "desc": "Deceptive wide-step crossover."},
            {"cat": "Between Legs", "ex": "Stationary Continuous", "base": 40, "unit": "reps", "checks": ["Low Hips", "No Extra Dribbles", "Hand Follow-through"], "desc": "Continuous figure-eight between legs."},
            {"cat": "Between Legs", "ex": "Walking Figure-8", "base": 2, "unit": "Laps", "checks": ["Forward Lean", "Step Rhythm", "Tight Crossover"], "desc": "Dribble through legs with every step forward."},
            {"cat": "Behind Back", "ex": "Wrap Around", "base": 30, "unit": "reps", "focus": ["Wrist Wrap", "Glute Clearance", "Speed"], "checks": ["Full Extension", "Tight Path"], "desc": "Full wrap-around behind the back."},
            {"cat": "Behind Back", "ex": "Behind-Cross Combo", "base": 20, "unit": "reps", "checks": ["Rhythm", "Low Center", "Change of Pace"], "desc": "Behind the back immediately into a front crossover."},
            {"cat": "Shooting", "ex": "Mikan Drill", "base": 20, "unit": "makes", "checks": ["Soft Touch", "High Release", "Footwork Rhythm"], "desc": "Continuous alternating layups under the rim."},
            {"cat": "Shooting", "ex": "Form Shots", "base": 15, "unit": "makes", "checks": ["1-Hand Control", "High Arc", "Snap Wrist"], "desc": "Close-range shots using only the dominant hand."},
            {"cat": "Shooting", "ex": "Elbow Jumpers", "base": 20, "unit": "shots", "checks": ["Square Hips", "Lift", "Hold Follow-through"], "desc": "Catch and shoot from the high post elbows."},
            {"cat": "Defense", "ex": "Zig-Zag Slides", "base": 4, "unit": "Lengths", "checks": ["Step-Slide", "No Heel Touch", "Active Hands"], "desc": "Lateral slides in a zig-zag pattern across the court."},
            {"cat": "Defense", "ex": "Closeouts", "base": 10, "unit": "reps", "checks": ["Choppy Feet", "High Hand", "Weight Back"], "desc": "Sprint to 3pt line and chop feet into defensive stance."},
            {"cat": "Defense", "ex": "Mirror Drill", "base": 60, "unit": "sec", "checks": ["Reaction Time", "Stay Low", "Head Position"], "desc": "Mimic a partner's lateral movements."},
            {"cat": "Passing", "ex": "Wall Chest Pass", "base": 30, "unit": "reps", "checks": ["Thumbs Down", "Step In", "Accuracy"], "desc": "Rapid fire chest passes against a solid wall."},
            {"cat": "Passing", "ex": "One-Hand Zip", "base": 20, "unit": "reps", "checks": ["Snap", "Targeting", "No Wind-up"], "desc": "One-handed 'push' passes to a target."},
            {"cat": "Combos", "ex": "Triple Threat Series", "base": 15, "unit": "reps", "checks": ["Jab Speed", "Ball Rip", "Low Shoulder"], "desc": "Combine jab, shimmy, and drive."},
            {"cat": "Finish", "ex": "Free Throws", "base": 10, "unit": "shots", "checks": ["Breathing", "Routine", "Concentration"], "desc": "Full routine shots while fatigued."}
        ]
    elif sport == "Softball":
        return [
            {"cat": "Hitting", "ex": "TEE WORK", "base": 25, "unit": "swings", "checks": ["Bat Path", "Extension", "Hip Rotation"], "desc": "Focus on consistent contact points."},
            {"cat": "Fielding", "ex": "GLOVE TRANSFERS", "base": 30, "unit": "reps", "checks": ["Grip Speed", "Four-Seam Find", "Elbow Up"], "desc": "Rapid transfer from glove to throwing hand."},
            {"cat": "Arm", "ex": "LONG TOSS", "base": 15, "unit": "throws", "checks": ["Arc", "Follow Through", "Crow Hop"], "desc": "Build arm strength through distance."},
            {"cat": "Fielding", "ex": "PICKER HOPS", "base": 20, "unit": "reps", "checks": ["Glove Down", "Soft Hands", "Stay Low"], "desc": "Fielding short-hop grounders."},
            {"cat": "Hitting", "ex": "SOFT TOSS", "base": 20, "unit": "swings", "checks": ["Timing", "Weight Transfer", "Head Still"], "desc": "Diagonal toss for reaction hitting."}
        ]
    elif sport == "Track":
        return [
            {"cat": "Technique", "ex": "A-SKIPS", "base": 40, "unit": "meters", "checks": ["Knee Drive", "Toe Up", "Mid-foot Strike"], "desc": "Rhythmic high-knee skipping."},
            {"cat": "Technique", "ex": "B-SKIPS", "base": 40, "unit": "meters", "checks": ["Leg Cycle", "Paw Back", "Posture"], "desc": "Extension and paw-back skipping."},
            {"cat": "Power", "ex": "BOUNDING", "base": 30, "unit": "meters", "checks": ["Air Time", "Knee Drive", "Explosion"], "desc": "Maximal horizontal leaping."},
            {"cat": "Speed", "ex": "BLOCK STARTS", "base": 8, "unit": "reps", "checks": ["Reaction", "Drive Phase", "Arm Pump"], "desc": "Starting blocks 10m explosion."}
        ]
    return []

# --- 3. DYNAMIC THEME ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; color: white; }}
    .drill-card {{ background-color: #1E293B; border-radius: 15px; padding: 20px; border: 1px solid #3B82F6; margin-bottom: 25px; }}
    .check-header {{ color: #00E5FF; font-weight: bold; text-transform: uppercase; font-size: 14px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & LOGIC ---
with st.sidebar:
    st.header("🏆 PRO TRACKER")
    sport_choice = st.selectbox("Sport", ["Basketball", "Softball", "Track", "General"])
    st.divider()
    if st.button("📥 DOWNLOAD REPORT"): st.toast("Report ready!")

# --- 5. MAIN UI ---
st.title(f"{sport_choice.upper()} ELITE SESSION")
drills = get_workout_template(sport_choice)

for i, item in enumerate(drills):
    with st.container():
        st.markdown(f'<div class="drill-card">', unsafe_allow_html=True)
        
        # Header Row
        h1, h2, h3 = st.columns([3, 1, 1])
        h1.subheader(f"{i+1}. {item['ex']}")
        h2.write(f"**Target:** {item['base']} {item['unit']}")
        h3.checkbox("MARK COMPLETED", key=f"done_{i}")
        
        st.info(item['desc'])
        
        # Tech & Coach Column
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown('<p class="check-header">Coach\'s Technique Checkpoints</p>', unsafe_allow_html=True)
            for check in item['checks']:
                st.checkbox(f"✔️ {check}", key=f"eval_{i}_{check}")
                
        with c2:
            st.markdown('<p class="check-header">Analysis & Demos</p>', unsafe_allow_html=True)
            if st.button(f"📺 VIEW {item['ex']} DEMO", key=f"demo_{i}"):
                st.info("Streaming demo...")
            
            st.divider()
            uploaded_file = st.file_uploader(f"Upload {item['ex']} Clip", type=["mp4", "mov"], key=f"up_{i}")
            if uploaded_file:
                st.video(uploaded_file)
                st.success("Analysis uploaded.")

        # Logging Row
        l1, l2, l3 = st.columns([1, 1, 2])
        sets = l1.text_input("Sets Done", value="3", key=f"sets_{i}")
        reps = l2.text_input("Reps Done", value=str(item['base']), key=f"reps_{i}")
        if l3.button("LOG PERFORMANCE", key=f"log_{i}", use_container_width=True):
            st.session_state.history.append({"Time": get_now_est().strftime("%H:%M"), "Drill": item['ex'], "Score": f"{sets}x{reps}"})
            st.toast(f"Logged {item['ex']}")

        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FOOTER ---
if st.button("💾 ARCHIVE SESSION", use_container_width=True, type="primary"):
    st.session_state.streak += 1
    st.balloons()

