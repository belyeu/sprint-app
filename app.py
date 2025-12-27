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

# Sidebar Toggle for Dark Mode
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Define Colors
if dark_mode:
    bg_color = "#0F172A"       # Deep Navy
    text_color = "#FFFFFF"     # Pure White
    accent_color = "#3B82F6"   # Athletic Blue
    header_bg = "#334155"      # Steel Gray
    sidebar_bg = "#1E293B"     # Slate
    sidebar_text = "#FFFFFF"
    input_bg = "#1E293B" 
    sport_text_color = "#000000" 
    numeric_color = "#60A5FA"  # Light Blue for Typed Text
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"     # Pure Black
    accent_color = "#1E40AF"   # Deep Athletic Blue
    header_bg = "#E2E8F0"      # Light Steel
    sidebar_bg = "#F8FAFC"
    sidebar_text = "#000000"
    input_bg = "#FFFFFF"
    sport_text_color = "#FFFFFF" 
    numeric_color = "#000000"  # Pure Black for iPhone

st.markdown(f"""
    <style>
    /* Global Text and Background */
    .stApp {{ background-color: {bg_color} !important; }}
    .main .block-container {{ padding-left: 5rem; padding-right: 2rem; background-color: {bg_color}; }}
    
    /* Sidebar Fixes */
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
        color: {sidebar_text} !important;
        -webkit-text-fill-color: {sidebar_text} !important;
    }}

    /* Global Text Visibility (iPhone) */
    h1, h2, h3, p, span, label, [data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        opacity: 1 !important;
    }}

    /* Numeric Inputs & Stat Values */
    .stat-value, [data-testid="stNumericInput"] input, [role="slider"] {{
        color: {numeric_color} !important;
        -webkit-text-fill-color: {numeric_color} !important;
        font-weight: 900 !important;
    }}

    /* Drill Headers */
    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent_color} !important;
        -webkit-text-fill-color: {accent_color} !important;
        text-transform: uppercase; margin-top: 30px; border-left: 10px solid {accent_color};
        padding: 10px 15px; background-color: {header_bg}; border-radius: 0 10px 10px 0;
    }}

    .drill-desc {{
        font-size: 16px !important; font-style: italic; color: {text_color} !important;
        margin-bottom: 20px; padding-left: 25px;
    }}

    /* NEW: Expander (Demo & Upload) Stylings */
    [data-testid="stExpander"] {{
        background-color: {input_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary p {{
        color: {accent_color} !important;
        -webkit-text-fill-color: {accent_color} !important;
        font-weight: 800 !important;
    }}
    [data-testid="stExpander"] svg {{
        fill: {accent_color} !important;
    }}

    /* File Uploader Customization */
    [data-testid="stFileUploader"] {{
        background-color: {header_bg} !important;
        border-radius: 10px !important;
        padding: 10px;
    }}

    /* Buttons & Progress */
    .stButton>button {{ 
        background-color: {accent_color} !important; color: white !important; 
        border-radius: 10px !important; font-weight: 800 !important; 
        width: 100%; height: 55px !important;
    }}
    .timer-text {{
        font-size: 60px !important; font-weight: bold !important; color: {accent_color} !important;
        text-align: center; font-family: 'Courier New', monospace; border: 4px solid {accent_color}; padding: 10px;
    }}
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; 
        border: 2px solid {accent_color}; background-color: {sidebar_bg};
    }}
    div[data-testid="stProgress"] > div > div > div > div {{
        background-color: {accent_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. Sidebar Setup ---
now = datetime.now()
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">SESSION START</p>
    <p style="margin:0; font-size:16px; font-weight:700;">{now.strftime("%B %d, %Y")}</p>
    <p style="margin:0; font-size:24px; font-weight:900;">{now.strftime("%I:%M %p")}</p>
</div>
""", unsafe_allow_html=True)

goal = 20
progress = min(st.session_state.monthly_sessions / goal, 1.0)
st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">{now.strftime("%B").upper()} GOAL</p>
    <p style="font-size:28px; font-weight:900; margin:0;">{st.session_state.monthly_sessions} / {goal}</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.progress(progress)

st.sidebar.markdown(f"""
<div class="sidebar-card">
    <p style="margin:0; font-weight:800; font-size:12px; color:{accent_color};">STREAK</p>
    <p style="font-size:32px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
sport_choice = st.sidebar.selectbox("Select Sport", ["Basketball", "Track", "Softball", "General Workout"])
difficulty = st.sidebar.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")

target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = 1.0 if difficulty == "Standard" else 1.1 if difficulty == "Elite" else 1.2

# --- 3. Workout Database ---
def get_workout_template(sport):
    workouts = {
        "Basketball": [
            {"ex": "POUND SERIES", "desc": "Stationary dribbling focusing on maximum force and ball control.", "sets": 3, "base": 60, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=akSJjN8UIj0", "eval": ["Low Stance", "Eyes Up"]},
            {"ex": "MIKAN SERIES", "desc": "Continuous layups under the rim alternating hands for touch.", "sets": 4, "base": 20, "unit": "reps", "rest": 45, "vid": "https://www.youtube.com/watch?v=3-8H85P6Kks", "eval": ["Soft Touch", "High Finish"]},
            {"ex": "FIGURE 8", "desc": "Weave the ball between your legs in a figure 8 motion.", "sets": 3, "base": 45, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=XpG0oE_A6k0", "eval": ["Ball Control", "Quick Hands"]},
            {"ex": "FREE THROWS", "desc": "Static shooting practice focusing on routine and follow-through.", "sets": 5, "base": 10, "unit": "makes", "rest": 60, "vid": "https://www.youtube.com/watch?v=R4-fR8_mXAc", "eval": ["Routine", "Follow Through"]},
            {"ex": "V-DRIBBLE", "desc": "Push and pull the ball in a V-shape in front of your body.", "sets": 3, "base": 50, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=2fS_Vp9fF8E", "eval": ["Wide Dribble", "Speed"]},
            {"ex": "DEFENSIVE SLIDES", "desc": "Lateral movement drill focusing on hip height and footwork.", "sets": 4, "base": 30, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=pAnVmqk-G9I", "eval": ["Low Hips", "Chest Up"]},
            {"ex": "BOX JUMPS", "desc": "Explosive vertical jumps onto a raised platform.", "sets": 3, "base": 12, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=52r6I-z6r-I", "eval": ["Explosive", "Soft Landing"]},
            {"ex": "WALL SITS", "desc": "Isostatic leg strength hold against a vertical flat surface.", "sets": 3, "base": 60, "unit": "sec", "rest": 60, "vid": "https://www.youtube.com/watch?v=y-wV4Venusw", "eval": ["90 Degrees", "Back Flat"]}
        ],
        "Track": [
            {"ex": "ANKLE DRIBBLES", "desc": "Small steps focusing on ankle dorsiflexion.", "sets": 3, "base": 30, "unit": "meters", "rest": 30, "vid": "https://www.youtube.com/watch?v=jmGox3HQvZw", "eval": ["Toes Up", "Quiet Hips"]},
            {"ex": "A-SKIPS", "desc": "Rhythmic skipping drill emphasizing knee drive.", "sets": 4, "base": 40, "unit": "meters", "rest": 45, "vid": "https://www.youtube.com/watch?v=r19U_fLgU2Y", "eval": ["Aggressive Strike", "Arm Drive"]},
            {"ex": "BOUNDING", "desc": "Explosive horizontal jumps focusing on flight time and power.", "sets": 3, "base": 30, "unit": "meters", "rest": 90, "vid": "https://www.youtube.com/watch?v=8V75e58P7oY", "eval": ["Hang Time", "Active Arms"]},
            {"ex": "HIGH KNEES", "desc": "Rapid vertical knee lifts focusing on frequency.", "sets": 3, "base": 20, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=ZZpDqXitvJ0", "eval": ["Parallel Thighs", "Midfoot Strike"]},
            {"ex": "ACCELERATIONS", "desc": "Short bursts focusing on the drive phase.", "sets": 6, "base": 20, "unit": "meters", "rest": 120, "vid": "https://www.youtube.com/watch?v=9_p5_1q6-vM", "eval": ["Low Start", "Drive Phase"]},
            {"ex": "SINGLE LEG HOPS", "desc": "Unilateral vertical jumps for stability.", "sets": 3, "base": 10, "unit": "reps/leg", "rest": 60, "vid": "https://www.youtube.com/watch?v=rI9XkU_o1f0", "eval": ["Elasticity", "Stable Ankle"]},
            {"ex": "RUSSIAN TWISTS", "desc": "Seated core rotation focusing on oblique strength.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=wkD8rjkodUI", "eval": ["Controlled", "Feet Up"]},
            {"ex": "HILL SPRINTS", "desc": "Max effort uphill runs for posterior chain power.", "sets": 5, "base": 10, "unit": "sec", "rest": 90, "vid": "https://www.youtube.com/watch?v=fXvYw0iSAn4", "eval": ["Lean Forward", "High Effort"]}
        ],
        "Softball": [
            {"ex": "TEE WORK", "desc": "Stationary hitting practice for mechanics.", "sets": 4, "base": 25, "unit": "swings", "rest": 60, "vid": "https://www.youtube.com/watch?v=Kz6XU0-z8_Y", "eval": ["Hip Rotation", "Eye on Contact"]},
            {"ex": "GLOVE TRANSFERS", "desc": "Rapid ball transfer from glove to hand.", "sets": 3, "base": 30, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=F07N8iL-G3U", "eval": ["Clean Pull", "Fast Grip"]},
            {"ex": "FRONT TOSS", "desc": "Short distance underhand toss for timing.", "sets": 4, "base": 20, "unit": "swings", "rest": 60, "vid": "https://www.youtube.com/watch?v=vV0I2uC_n68", "eval": ["Weight Transfer", "Short Path"]},
            {"ex": "LATERAL SHUFFLES", "desc": "Quick lateral movements for defensive range.", "sets": 3, "base": 30, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=uK48_lK-n5w", "eval": ["Stay Low", "Ready Position"]},
            {"ex": "LONG TOSS", "desc": "Maximum distance throwing to build arm strength.", "sets": 3, "base": 15, "unit": "throws", "rest": 60, "vid": "https://www.youtube.com/watch?v=4y-iP_N9eE8", "eval": ["Full Extension", "Accuracy"]},
            {"ex": "WRIST SNAPS", "desc": "Forearm focus to increase ball velocity.", "sets": 3, "base": 20, "unit": "reps", "rest": 30, "vid": "https://www.youtube.com/watch?v=M57O_4wJq0I", "eval": ["Quick Snap", "Follow Through"]},
            {"ex": "SQUAT JUMPS", "desc": "Lower body power drill for explosive speed.", "sets": 3, "base": 12, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=72BSZupb-1I", "eval": ["Explosive Up", "Soft Landing"]},
            {"ex": "SPRINT TO FIRST", "desc": "Full speed running drill from home plate.", "sets": 6, "base": 1, "unit": "sprint", "rest": 45, "vid": "https://www.youtube.com/watch?v=B70FfBInA3w", "eval": ["Turn Corner", "Finish Strong"]}
        ],
        "General Workout": [
            {"ex": "GOBLET SQUATS", "desc": "Weighted squats for core tension and leg depth.", "sets": 4, "base": 12, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=MeIiGibT69I", "eval": ["Depth", "Chest Up"]},
            {"ex": "PUSHUPS", "desc": "Upper body press for chest and tricep strength.", "sets": 3, "base": 15, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=IODxDxX7oi4", "eval": ["Core Tight", "Full Lockout"]},
            {"ex": "LUNGES", "desc": "Unilateral leg movement for balance.", "sets": 3, "base": 10, "unit": "reps/leg", "rest": 60, "vid": "https://www.youtube.com/watch?v=L8fvypPrzzs", "eval": ["Balance", "Upright"]},
            {"ex": "PLANK", "desc": "Static core hold focusing on total body tension.", "sets": 3, "base": 45, "unit": "sec", "rest": 45, "vid": "https://www.youtube.com/watch?v=pSHjTRCQxIw", "eval": ["Flat Back", "Glutes Engaged"]},
            {"ex": "DUMBBELL ROW", "desc": "Unilateral pulling movement for back strength.", "sets": 4, "base": 12, "unit": "reps", "rest": 60, "vid": "https://www.youtube.com/watch?v=6KA7SFr8P4E", "eval": ["Elbow High", "Still Torso"]},
            {"ex": "MOUNTAIN CLIMBERS", "desc": "High intensity dynamic movement for core and cardio.", "sets": 3, "base": 30, "unit": "sec", "rest": 30, "vid": "https://www.youtube.com/watch?v=nmwgirgXLYM", "eval": ["Fast Pace", "Knees High"]},
            {"ex": "GLUTE BRIDGES", "desc": "Floor movement targeting glute isolation.", "sets": 3, "base": 15, "unit": "reps", "rest": 45, "vid": "https://www.youtube.com/watch?v=wPM8icPu6H8", "eval": ["Squeeze Glutes", "Heels Down"]},
            {"ex": "BURPEES", "desc": "Full body explosive movement for endurance.", "sets": 3, "base": 10, "unit": "reps", "rest": 90, "vid": "https://www.youtube.com/watch?v=dZfeV_pL3fE", "eval": ["Full Jump", "Fast Tempo"]}
        ]
    }
    return workouts.get(sport, [])

# --- 4. Main UI ---
st.markdown(f"<h1>{sport_choice} Session</h1>", unsafe_allow_html=True)
drills = get_workout_template(sport_choice)

for i in range(len(drills)):
    item = drills[i]
    drill_key = f"{sport_choice}_{i}"
    if drill_key not in st.session_state: st.session_state[drill_key] = 0
    
    st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="drill-desc">{item["desc"]}</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<p class="stat-label">Target Sets</p><p class="stat-value">{item["sets"]}</p>', unsafe_allow_html=True)
    with c2:
        rv = int(item['base'] * target_mult)
        st.markdown(f'<p class="stat-label">Reps/Time</p><p class="stat-value">{rv} {item["unit"]}</p>', unsafe_allow_html=True)
    with c3: st.markdown(f'<p class="stat-label">Completed</p><p class="stat-value">{st.session_state[drill_key]}</p>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"DONE ✅", key=f"done_{i}"):
            st.session_state[drill_key] += 1
            st.rerun()
    with col_b:
        if st.button(f"REST ⏱️", key=f"rest_{i}"):
            fr = int(item['rest'] * rest_mult)
            ph = st.empty()
            for t in range(fr, -1, -1):
                ph.markdown(f'<p class="timer-text">{t//60:02d}:{t%60:02d}</p>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state[drill_key] += 1
            st.rerun()

    st.markdown("### 📋 COACH'S EVALUATION")
    eval_cols = st.columns(2)
    for idx, crit in enumerate(item['eval']):
        eval_cols[idx % 2].checkbox(crit, key=f"ev_{drill_key}_{idx}")
    
    st.select_slider("Intensity (RPE)", options=range(1, 11), value=8, key=f"rpe_{drill_key}")
    st.text_input("Notes", key=f"note_{drill_key}")

    with st.expander("🎥 DEMO & UPLOAD"):
        st.video(item['vid'])
        st.file_uploader("Upload Clip", type=["mp4", "mov"], key=f"up_{i}")

st.divider()
cs, cr = st.columns(2)
with cs:
    if st.button("💾 SAVE WORKOUT"):
        st.balloons()
        st.session_state.streak += 1
        st.session_state.monthly_sessions += 1
        st.session_state.session_saved = True
        st.rerun()
with cr:
    if st.button("🔄 RESET SESSION"):
        for i in range(len(drills)): st.session_state[f"{sport_choice}_{i}"] = 0
        st.session_state.session_saved = False
        st.rerun()

if st.session_state.session_saved:
    st.success("Session saved!")
    st.markdown('<div class="drill-header">⚡ RECOVERY CHECKLIST</div>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    with rc1:
        st.checkbox("Hydration (20oz+ Water)")
        st.checkbox("Protein (20-40g)")
    with rc2:
        st.checkbox("Stretching (10 min)")
        st.checkbox("Log Sleep Quality")
