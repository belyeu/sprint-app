import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. High-Visibility Theme Configuration ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide")

# Initialize Session State
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'session_saved' not in st.session_state: 
    st.session_state.session_saved = False
if 'monthly_sessions' not in st.session_state:
    st.session_state.monthly_sessions = 0

# Sidebar Toggle
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors for iPhone Rendering
if dark_mode:
    bg_color = "#0F172A"       # Deep Navy
    text_color = "#FFFFFF"     # Pure White
    accent_color = "#3B82F6"   # Athletic Blue
    header_bg = "#1E293B"      # Dark Slate
    input_text = "#60A5FA"     # Light Blue for Input
    card_bg = "#1E293B"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"     # Pure Black
    accent_color = "#1E40AF"   # Deep Athletic Blue
    header_bg = "#F1F5F9"      # Light Gray
    input_text = "#000000"
    card_bg = "#F8FAFC"

st.markdown(f"""
    <style>
    /* 1. Global Reset for iPhone Safari Visibility */
    .stApp {{ background-color: {bg_color} !important; }}
    
    h1, h2, h3, p, span, label, div {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        opacity: 1 !important;
    }}

    /* 2. Fix the Gray "Demo & Upload" (Expander) Box */
    [data-testid="stExpander"] {{
        background-color: {header_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: 12px !important;
    }}
    
    details summary p {{
        color: {accent_color} !important;
        -webkit-text-fill-color: {accent_color} !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }}

    /* 3. Fix the File Uploader Gray Area */
    [data-testid="stFileUploader"] section {{
        background-color: {bg_color} !important;
        border: 2px dashed {accent_color} !important;
        border-radius: 10px !important;
    }}
    
    /* 4. Inputs and Text Areas */
    input, textarea {{
        background-color: {header_bg} !important;
        color: {input_text} !important;
        -webkit-text-fill-color: {input_text} !important;
    }}

    /* 5. Headers & Branding */
    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; color: {accent_color} !important;
        -webkit-text-fill-color: {accent_color} !important;
        background-color: {header_bg}; border-left: 10px solid {accent_color};
        padding: 12px; border-radius: 0 10px 10px 0; margin-top: 25px;
    }}

    .stat-label {{ font-size: 14px !important; font-weight: 800 !important; color: {accent_color} !important; text-transform: uppercase; }}
    .stat-value {{ font-size: 32px !important; font-weight: 900 !important; margin-bottom: 5px; }}
    
    /* 6. High-Visibility Buttons */
    .stButton>button {{ 
        background-color: {accent_color} !important; color: white !important; 
        -webkit-text-fill-color: white !important;
        border-radius: 10px !important; font-weight: 800 !important; height: 55px !important;
    }}
    
    .timer-text {{
        font-size: 50px !important; font-weight: bold !important; color: {accent_color} !important;
        text-align: center; font-family: monospace; border: 4px solid {accent_color}; padding: 10px;
    }}
    
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 2px solid {accent_color}; 
        background-color: {card_bg}; text-align: center; margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Master Database ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Stationary dribbling focusing on maximum force.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Eyes Up"]},
            {"ex": "MIKAN SERIES", "desc": "Continuous layups under the rim alternating hands.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["Soft Touch", "High Finish"]},
            {"ex": "FIGURE 8", "desc": "Weave ball between legs in a figure 8 motion.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Ball Control", "Quick Hands"]},
            {"ex": "FREE THROWS", "desc": "Static shooting practice focusing on routine.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "vid": "https://www.youtube.com/watch?v=R4-fR8_mXAc", "eval": ["Routine", "Follow Through"]},
            {"ex": "V-DRIBBLE", "desc": "Push and pull the ball in a V-shape in front of body.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "eval": ["Wide Dribble", "Speed"]},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral movement focusing on hip height.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=pAnVmqk-G9I", "eval": ["Low Hips", "Chest Up"]},
            {"ex": "BOX JUMPS", "desc": "Explosive vertical jumps onto platform.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=52r6I-z6r-I", "eval": ["Explosive", "Soft Landing"]},
            {"ex": "WALL SITS", "desc": "Isostatic leg strength hold.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "vid": "https://www.youtube.com/watch?v=y-wV4Venusw", "eval": ["90 Degrees", "Back Flat"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Small steps focusing on ankle dorsiflexion.", "sets": 3, "base": 30, "unit": "meters", "rest": 30, "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Quiet Hips"]},
            {"ex": "A-SKIPS", "desc": "Rhythmic skipping emphasizing knee drive.", "sets": 4, "base": 40, "unit": "meters", "rest": 45, "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Drive"]},
            {"ex": "BOUNDING", "desc": "Explosive horizontal jumps.", "sets": 3, "base": 30, "unit": "meters", "rest": 90, "vid": "https://www.youtube.com/watch?v=8V75e58P7oY", "eval": ["Hang Time", "Active Arms"]},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical knee lifts.", "sets": 3, "base": 20, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=ZZpDqXitvJ0", "eval": ["Parallel Thighs", "Midfoot Strike"]},
            {"ex": "ACCELERATIONS", "desc": "Short bursts focusing on drive phase.", "sets": 6, "base": 20, "unit": "meters", "rest": 120, "vid": "https://www.youtube.com/watch?v=9_p5_1q6-vM", "eval": ["Low Start", "Drive Phase"]},
            {"ex": "SINGLE LEG HOPS", "desc": "Unilateral jumps for stability.", "sets": 3, "base": 10, "unit": "reps/leg", "rest": 60, "vid": "https://www.youtube.com/watch?v=rI9XkU_o1f0", "eval": ["Elasticity", "Stable Ankle"]},
            {"ex": "RUSSIAN TWISTS", "desc": "Seated core rotation.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=wkD8rjkodUI", "eval": ["Controlled", "Feet Up"]},
            {"ex": "HILL SPRINTS", "desc": "Max effort uphill runs.", "sets": 5, "base": 10, "unit": "sec", "rest": 90, "vid": "https://www.youtube.com/watch?v=fXvYw0iSAn4", "eval": ["Lean Forward", "High Effort"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Stationary hitting for mechanics.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact"]},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid ball transfer from glove.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Clean Pull", "Fast Grip"]},
            {"ex": "FRONT TOSS", "desc": "Short distance toss for timing.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "vid": "https://www.youtube.com/watch?v=vV0I2uC_n68", "eval": ["Weight Transfer", "Short Path"]},
            {"ex": "LATERAL SHUFFLES", "desc": "Quick movement for range.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=uK48_lK-n5w", "eval": ["Stay Low", "Ready Position"]},
            {"ex": "LONG TOSS", "desc": "Maximum distance throwing.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "vid": "https://www.youtube.com/watch?v=4y-iP_N9eE8", "eval": ["Full Extension", "Accuracy"]},
            {"ex": "WRIST SNAPS", "desc": "Forearm focus for velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=M57O_4wJq0I", "eval": ["Quick Snap", "Follow Through"]},
            {"ex": "SQUAT JUMPS", "desc": "Explosive first-step speed.", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=72BSZupb-1I", "eval": ["Explosive Up", "Soft Landing"]},
            {"ex": "SPRINT TO FIRST", "desc": "Full speed running drill.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "vid": "https://www.youtube.com/watch?v=B70FfBInA3w", "eval": ["Turn Corner", "Finish Strong"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Weighted squats for depth.", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up"]},
            {"ex": "PUSHUPS", "desc": "Upper body press strength.", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout"]},
            {"ex": "LUNGES", "desc": "Unilateral movement for balance.", "sets": 3, "base": 10, "unit": "reps/leg", "rest": 60, "vid": "https://www.youtube.com/watch?v=L8fvypPrzzs", "eval": ["Balance", "Upright"]},
            {"ex": "PLANK", "desc": "Static core tension hold.", "sets": 3, "base": 45, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=pSHjTRCQxIw", "eval": ["Flat Back", "Glutes Engaged"]},
            {"ex": "DUMBBELL ROW", "desc": "Unilateral back strength.", "sets": 4, "base": 12, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=6KA7SFr8P4E", "eval": ["Elbow High", "Still Torso"]},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "High intensity dynamic core.", "sets": 3, "base": 30, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=nmwgirgXLYM", "eval": ["Fast Pace", "Knees High"]},
            {"ex": "GLUTE BRIDGES", "desc": "Glute isolation movement.", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "vid": "https://www.youtube.com/watch?v=wPM8icPu6H8", "eval": ["Squeeze Glutes", "Heels Down"]},
            {"ex": "BURPEES", "desc": "Full body explosive power.", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=dZfeV_pL3fE", "eval": ["Full Jump", "Fast Tempo"]}
        ]
    }
    return workouts.get(sport, [])

# --- 3. Sidebar Configuration ---
now = datetime.now()
st.sidebar.markdown(f'<div class="sidebar-card"><p style="color:{accent_color}; font-size:12px; margin:0;">STREAK</p><p style="font-size:24px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p></div>', unsafe_allow_html=True)

sport_choice = st.sidebar.selectbox("Select Sport", list(["Basketball", "Track", "Softball", "General Workout"]))
difficulty = st.sidebar.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 4. Main UI Logic ---
st.markdown(f"<h1>{sport_choice} Session</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

for i, item in enumerate(drills):
    drill_key = f"{sport_choice}_{i}"
    if drill_key not in st.session_state: st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-style:italic; margin-top:10px; margin-bottom:20px;">{item["desc"]}</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<p class="stat-label">Sets</p><p class="stat-value">{item["sets"]}</p>', unsafe_allow_html=True)
    with c2:
        val = int(item['base'] * target_mult)
        st.markdown(f'<p class="stat-label">Target</p><p class="stat-value">{val} {item["unit"]}</p>', unsafe_allow_html=True)
    with c3: st.markdown(f'<p class="stat-label">Done</p><p class="stat-value">{st.session_state[drill_key]}</p>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"DONE ✅", key=f"done_{i}", use_container_width=True):
            st.session_state[drill_key] += 1
            st.rerun()
    with col_b:
        if st.button(f"REST ⏱️", key=f"rest_{i}", use_container_width=True):
            fr = int(item['rest'] * rest_mult)
            ph = st.empty()
            for t in range(fr, -1, -1):
                ph.markdown(f'<p class="timer-text">{t//60:02d}:{t%60:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state[drill_key] += 1
            st.rerun()

    # Evaluation Section
    st.markdown("### 📋 COACH'S EVAL")
    ec1, ec2 = st.columns(2)
    for idx, crit in enumerate(item['eval']):
        (ec1 if idx % 2 == 0 else ec2).checkbox(crit, key=f"ev_{drill_key}_{idx}")
    
    st.text_input("Notes", key=f"note_{drill_key}", placeholder="How did this set feel?")

    # iPhone Fixed Expander
    with st.expander("🎥 DEMO & UPLOAD"):
        st.video(item['vid'])
        st.file_uploader("Upload Video", type=["mp4", "mov"], key=f"up_{i}")

st.divider()

if st.button("💾 SAVE WORKOUT", key="final_save", use_container_width=True):
    st.balloons()
    st.session_state.streak += 1
    st.session_state.monthly_sessions += 1
    st.session_state.session_saved = True
    st.rerun()

if st.session_state.session_saved:
    st.success("Session saved successfully!")
