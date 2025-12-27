import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime

# --- Theme & Style Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #013220; color: #ffffff; }
    .drill-header {
        font-size: 34px !important;
        font-weight: 900 !important;
        color: #FFD700 !important;
        text-transform: uppercase;
        margin-bottom: 5px;
        margin-top: 30px;
        font-family: 'Arial Black', sans-serif;
        border-left: 10px solid #FFD700;
        padding-left: 20px;
    }
    .timer-text {
        font-size: 85px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        background: #004d26;
        border-radius: 12px;
        border: 4px solid #FFD700;
        padding: 15px;
    }
    .stButton>button { 
        background-color: #FFD700; 
        color: #013220; 
        border-radius: 10px; 
        font-weight: bold; 
        border: 2px solid #DAA520; 
        width: 100%; 
        height: 60px;
        font-size: 22px;
    }
    .stMetric { 
        background-color: #004d26; 
        padding: 20px; 
        border-radius: 12px; 
        border: 3px solid #FFD700; 
    }
    h1 { color: #FFD700 !important; font-size: 52px !important; text-align: center; border-bottom: 5px solid #FFD700; padding-bottom: 15px; text-transform: uppercase; }
    .coach-notes { background-color: #ffd70022; padding: 10px; border-radius: 5px; border-left: 3px solid #FFD700; margin-bottom: 10px; }
    .recovery-card { background-color: #004d26; border: 2px solid #FFD700; padding: 20px; border-radius: 15px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "base": 60, "inc": 15, "unit": "seconds", "rest": 30, "type": "cond", "desc": "Hard, explosive dribbles at hip, knee, and ankle height. Keep eyes up.", "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0"},
            {"ex": "FIGURE 8 SERIES", "base": 90, "inc": 20, "unit": "seconds", "rest": 30, "type": "cond", "desc": "Low dribbles in a figure-8 pattern around legs. Focus on fingertip control.", "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0"},
            {"ex": "STATIONARY CROSSOVER", "base": 100, "inc": 25, "unit": "reps", "rest": 45, "type": "power", "desc": "Wide crossovers outside the frame of your body. Snap the ball across.", "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E"},
            {"ex": "MOVING CROSSOVER", "base": 10, "inc": 2, "unit": "trips", "rest": 60, "type": "power", "desc": "Full court trips using change of pace and direction at each line.", "vid": "https://www.youtube.com/watch?v=RInYn_KszpQ"},
            {"ex": "LATERAL DEFENSIVE SLIDES", "base": 8, "inc": 2, "unit": "trips", "rest": 90, "type": "power", "desc": "Stay low, chest up, do not cross feet. Push off the trail leg.", "vid": "https://www.youtube.com/watch?v=0kFvYF2V_W0"},
            {"ex": "FLOAT DRIBBLE SERIES", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power", "desc": "Use a skip step to 'float' laterally while keeping the ball in your pocket.", "vid": "https://www.youtube.com/watch?v=G-ylr5AQExw"},
            {"ex": "SLIDE TO FLOAT TRANSITION", "base": 30, "inc": 5, "unit": "reps", "rest": 60, "type": "power", "desc": "Defensive slide for 2 steps, then immediate transition into an offensive float.", "vid": "https://www.youtube.com/watch?v=Y-PbeO20oI0"},
            {"ex": "MIKAN SERIES", "base": 50, "inc": 10, "unit": "makes", "rest": 60, "type": "power", "desc": "Continuous layups alternating hands. Keep the ball above your head.", "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks"}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "base": 40, "inc": 10, "unit": "meters", "rest": 30, "type": "cond", "desc": "Quick steps with toes up. Movement comes from the ankles, not knees.", "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw"},
            {"ex": "A-MARCH", "base": 50, "inc": 10, "unit": "meters", "rest": 45, "type": "cond", "desc": "Focus on knee drive and opposite arm action. Stay tall.", "vid": "https://www.youtube.com/watch?v=1eX7v7S7eP0"},
            {"ex": "A-SKIP", "base": 60, "inc": 10, "unit": "meters", "rest": 60, "type": "power", "desc": "Aggressive foot strike under center of mass.", "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y"},
            {"ex": "WICKET RUNS", "base": 12, "inc": 2, "unit": "reps", "rest": 180, "type": "power", "desc": "Runs over low mini-hurdles to force upright posture.", "vid": "https://www.youtube.com/watch?v=lS69U9Zp4rI"},
            {"ex": "BLOCK STARTS", "base": 8, "inc": 2, "unit": "reps", "rest": 240, "type": "power", "desc": "Explosive exit from blocks.", "vid": "https://www.youtube.com/watch?v=hGv-1Mst0Cg"},
            {"ex": "MAX VELOCITY FLYS", "base": 6, "inc": 1, "unit": "reps", "rest": 300, "type": "power", "desc": "20-30m of maximum possible speed.", "vid": "https://www.youtube.com/watch?v=G66hT9W-9qI"},
            {"ex": "POWER SKIPS", "base": 50, "inc": 10, "unit": "meters", "rest": 60, "type": "power", "desc": "Aim for maximum height and hang time.", "vid": "https://www.youtube.com/watch?v=M9F0YpG7Eis"},
            {"ex": "SPEED ENDURANCE", "base": 5, "inc": 1, "unit": "reps", "rest": 120, "type": "cond", "desc": "Longer sprints (150m-200m) at 90% intensity.", "vid": "https://www.youtube.com/watch?v=5rLzHbeV9iM"}
        ],
        "Softball": [
            {"ex": "TEE SERIES", "base": 50, "inc": 15, "unit": "swings", "rest": 60, "type": "power", "desc": "Focus on hand path. Hit to all fields.", "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y"},
            {"ex": "FRONT TOSS POWER", "base": 40, "inc": 10, "unit": "swings", "rest": 120, "type": "power", "desc": "Drive through the ball with lower half engagement.", "vid": "https://www.youtube.com/watch?v=t_o7u-M6G-M"},
            {"ex": "GLOVE WORK (KNEES)", "base": 50, "inc": 10, "unit": "reps", "rest": 60, "type": "power", "desc": "Develop soft hands and quick transfers.", "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U"},
            {"ex": "INFIELD CHARGING", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power", "desc": "Attack the slow roller and field on the run.", "vid": "https://www.youtube.com/watch?v=68D0v7fWpT4"},
            {"ex": "BACKHAND/FOREHAND", "base": 30, "inc": 5, "unit": "reps", "rest": 90, "type": "power", "desc": "Lateral movement drills for footwork.", "vid": "https://www.youtube.com/watch?v=P_UvP0L8yXk"},
            {"ex": "BASERUNNING SPRINTS", "base": 12, "inc": 2, "unit": "sprints", "rest": 120, "type": "power", "desc": "Home to 1st and rounding 1st.", "vid": "https://www.youtube.com/watch?v=f-Bf0-uF-u4"},
            {"ex": "LATERAL AGILITY", "base": 10, "inc": 2, "unit": "sets", "rest": 60, "type": "cond", "desc": "Quick lateral shuffles between cones.", "vid": "https://www.youtube.com/watch?v=vV_XyR-7i0o"},
            {"ex": "FLY BALL TRACKING", "base": 20, "inc": 5, "unit": "reps", "rest": 60, "type": "cond", "desc": "Catch balls over the shoulder.", "vid": "https://www.youtube.com/watch?v=n7zG-pB_Y8M"}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "base": 15, "inc": 3, "unit": "reps", "rest": 120, "type": "power", "desc": "Hold weight at chest. Sit back into hips.", "vid": "https://www.youtube.com/watch?v=MeIiGibT69I"},
            {"ex": "PUSHUPS", "base": 25, "inc": 5, "unit": "reps", "rest": 90, "type": "power", "desc": "Full range of motion. Chest to floor.", "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4"},
            {"ex": "DUMBBELL ROWS", "base": 12, "inc": 2, "unit": "reps/arm", "rest": 90, "type": "power", "desc": "Pull weight to hip, squeeze shoulder blade.", "vid": "https://www.youtube.com/watch?v=roCP6wC47G0"},
            {"ex": "WALKING LUNGES", "base": 15, "inc": 2, "unit": "reps", "rest": 90, "type": "power", "desc": "Keep front knee over ankle.", "vid": "https://www.youtube.com/watch?v=D7KaRcUTQeE"},
            {"ex": "PLANK HOLD", "base": 60, "inc": 15, "unit": "seconds", "rest": 60, "type": "cond", "desc": "Maintain a straight line from head to heels.", "vid": "https://www.youtube.com/watch?v=ASdvN_XEl_c"},
            {"ex": "MED BALL SLAMS", "base": 20, "inc": 5, "unit": "reps", "rest": 60, "type": "power", "desc": "Slam ball down with full body power.", "vid": "https://www.youtube.com/watch?v=Rx_UHMnQljU"},
            {"ex": "BOX JUMPS", "base": 12, "inc": 2, "unit": "reps", "rest": 120, "type": "power", "desc": "Land softly with knees out.", "vid": "https://www.youtube.com/watch?v=52r_Ul5k03g"},
            {"ex": "MOUNTAIN CLIMBERS", "base": 60, "inc": 15, "unit": "seconds", "rest": 60, "type": "cond", "desc": "Drive knees to chest.", "vid": "https://www.youtube.com/watch?v=zT-9L37Re_8"}
        ]
    }
    return workouts.get(sport, [])

# --- Sidebar ---
st.sidebar.header("🥇 ATHLETE PROFILE")
sport = st.sidebar.selectbox("Choose Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
week_num = st.sidebar.number_input("Current Week", min_value=1, value=1)
session_num = st.sidebar.number_input("Session Number", min_value=1, value=1)

target_mult = 1.0 if difficulty == "Standard" else 1.5 if difficulty == "Elite" else 2.0
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- Workout UI ---
st.header(f"🔥 {sport} | Level: {difficulty}")
drills = get_workout_template(sport)

if 'session_saved' not in st.session_state:
    st.session_state.session_saved = False

for i, item in enumerate(drills):
    target_val = int((item['base'] + ((week_num - 1) * item['inc'])) * target_mult)
    final_rest = int(item['rest'] * rest_mult) if item['type'] == 'power' else int(item['rest'] / rest_mult)
        
    st.markdown(f'<p class="drill-header">{i+1}. {item["ex"]}</p>', unsafe_allow_html=True)
    
    with st.expander("DRILL DETAILS & LOGGING", expanded=True):
        st.markdown(f'<div class="coach-notes"><b>Coach\'s Notes:</b> {item["desc"]}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.metric("Target", f"{target_val} {item['unit']}")
            st.link_button("📺 Watch Video", item['vid'])
        with c2:
            mins, secs = divmod(final_rest, 60)
            rest_display = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
            st.write(f"**Optimal Rest:** {rest_display}")
            
            if st.button(f"⏱️ Start Timer", key=f"timer_{i}"):
                ph = st.empty()
                for t in range(final_rest, -1, -1):
                    m, s = divmod(t, 60)
                    ph.markdown(f'<p class="timer-text">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
                    time.sleep(1)
                st.success("GO!")
        with c3:
            st.text_input("Log Result", key=f"log_{i}")
            st.select_slider("RPE", options=range(1, 11), value=8, key=f"rpe_{i}")

st.divider()

if st.button("💾 SAVE SESSION DATA"):
    st.session_state.session_saved = True
    st.balloons()

if st.session_state.session_saved:
    st.markdown("""
        <div class="recovery-card">
            <h3>✅ SESSION COMPLETE! RECOVERY PROTOCOL:</h3>
            <ul>
                <li><b>Hydration:</b> Consume 16-24oz of water with electrolytes.</li>
                <li><b>Nutrition:</b> Eat a 3:1 Carb-to-Protein snack/meal within 45 mins.</li>
                <li><b>Soft Tissue:</b> 5-10 mins of foam rolling or static stretching.</li>
                <li><b>Mental:</b> Log one thing you did well and one to improve.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
