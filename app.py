import streamlit as st
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
