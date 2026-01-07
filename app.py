import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEME (HIGH CONTRAST & SAFARI FIX) ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue, sidebar_text, card_bg = "#00E5FF", "#FFFFFF", "#1E293B"
    metric_color = "#38BDF8"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue, sidebar_text, card_bg = "#006064", "#111111", "#F8FAFC"
    metric_color = "#1E40AF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    h1, h2, h3, p, span, label, li, .stMarkdown p {{ 
        color: {text} !important; 
        -webkit-text-fill-color: {text} !important;
        opacity: 1 !important;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important; font-weight: 800 !important;
    }}
    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent} !important;
        background-color: {header_bg}; border-left: 10px solid {accent};
        padding: 15px; border-radius: 0 12px 12px 0; margin-top: 35px;
    }}
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
        background-color: {card_bg}; text-align: center; margin-bottom: 15px;
    }}
    .focus-card {{
        background-color: {header_bg}; padding: 10px; border-radius: 8px;
        border: 1px solid {accent}; margin-bottom: 5px;
    }}
    .stButton>button {{
        background-color: {accent} !important; color: white !important;
        font-weight: 800 !important; border-radius: 10px !important;
        height: 3em;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CSV DATA ENGINE (ERROR PROOFED) ---
@st.cache_data
def load_drill_database():
    CSV_URL = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv"
    try:
        df = pd.read_csv(CSV_URL)
        # Clean column headers
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

def safe_int_convert(val, default=60):
    """Safely converts CSV values to integers, removing non-numeric characters."""
    try:
        if pd.isna(val): return default
        # Extract only digits (e.g., '30s' -> '30')
        numeric_part = re.sub(r'\D', '', str(val))
        return int(numeric_part) if numeric_part else default
    except:
        return default

def get_workout(df, sport, locs, multiplier):
    if df.empty:
        return []
    
    # Filtering Logic
    if 'Sport' in df.columns:
        mask = (df['Sport'].str.strip() == sport) & (df['Location'].isin(locs))
        filtered = df[mask]
    else:
        st.error("Column 'Sport' not found in CSV.")
        return []
    
    drills = []
    for _, row in filtered.iterrows():
        # Handle Scaling for Reps/Dist
        raw_goal = str(row.get('Reps/Dist', row.get('Reps', '10')))
        nums = re.findall(r'\d+', raw_goal)
        scaled_goal = raw_goal
        for n in nums:
            scaled_val = str(int(round(int(n) * multiplier)))
            scaled_goal = scaled_goal.replace(n, scaled_val, 1)

        # Build Drill Object with Safe Conversions
        drills.append({
            "ex": row.get('Exercise Name', row.get('Exercise', 'Unknown Drill')),
            "desc": row.get('Description', 'No description provided.'),
            "sets": int(round(safe_int_convert(row.get('Sets', 3)) * multiplier)),
            "goal": scaled_goal,
            "rest": safe_int_convert(row.get('Rest', 60)),
            "loc": row.get('Location', 'Gym'),
            "demo": row.get('Demo', row.get('Demo_URL', '')),
            "focus": str(row.get('Focus_Points', '')).split(';') if ';' in str(row.get('Focus_Points', '')) else [str(row.get('Focus_Points', ''))]
        })
    return drills

# --- 4. INITIALIZE ---
df_master = load_drill_database()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">EST TIME</p>
        <p style="margin:0; font-size:20px; font-weight:900;">{get_now_est().strftime('%I:%M %p')}</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(f'<div class="sidebar-card"><p style="color:{accent}; font-size:12px; margin:0;">STREAK</p><p style="font-size:24px; font-weight:900; margin:0;">{st.session_state.streak} DAYS</p></div>', unsafe_allow_html=True)

    app_mode = st.selectbox("Navigate System", ["Workout Plan", "Archive & History"])

    # Extract available sports
    if not df_master.empty and 'Sport' in df_master.columns:
        available_sports = sorted(df_master['Sport'].unique().tolist())
    else:
        available_sports = ["Basketball"]
        
    sport_choice = st.selectbox("Active Sport", available_sports)
    
    st.markdown("### 📍 FACILITY")
    gym_on = st.checkbox("Indoor Gym", value=True)
    track_on = st.checkbox("Outdoor Track", value=True)
    weight_on = st.checkbox("Weight Room", value=True)
    
    # Map checkbox labels to CSV Location values
    active_locs = []
    if gym_on: active_locs.append("Gym")
    if track_on: active_locs.append("Track")
    if weight_on: active_locs.append("Weight Room")
    
    intensity = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    scaling_factor = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[intensity]

# --- 6. CORE TRAINING ENGINE ---
if app_mode == "Workout Plan":
    st.title("PRO-ATHLETE TRACKER")
    
    session_drills = get_workout(df_master, sport_choice, active_locs, scaling_factor)

    if not session_drills:
        st.warning(f"No drills matching your filters found for {sport_choice}.")
    else:
        completed = 0
        for i, item in enumerate(session_drills):
            st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
            st.markdown(f"**Focus Area:** {item['loc']}")
            st.write(item["desc"])
            
            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("Planned Sets", value=str(item["sets"]), key=f"s_{i}")
            with c2: st.text_input("Target Goal", value=item['goal'], key=f"g_{i}")
            with c3: 
                if st.checkbox("Set Complete", key=f"c_{i}"): completed += 1

            if any(item["focus"]):
                st.markdown(f"<p style='color:{electric_blue}; font-weight:900;'>ELITE FOCUS</p>", unsafe_allow_html=True)
                f_cols = st.columns(len(item["focus"]))
                for idx, pt in enumerate(item["focus"]):
                    if pt.strip():
                        with f_cols[idx]: st.markdown(f'<div class="focus-card">🎯 {pt.strip()}</div>', unsafe_allow_html=True)

            timer_col, video_col = st.columns([2, 1])
            with timer_col:
                if st.button(f"⏱️ START {item['rest']}s RECOVERY", key=f"r_{i}"):
                    ph = st.empty()
                    for t in range(item['rest'], -1, -1):
                        ph.markdown(f"<h1 style='color:{metric_color}; text-align:center;'>{t}s</h1>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.empty()
                    st.success("RECOVERY COMPLETE!")

            with video_col:
                with st.expander("🎥 REFERENCE"):
                    if "http" in str(item["demo"]): st.video(item["demo"])
                    else: st.info("Visual Reference Unavailable")

        st.divider()
        if st.button("🏁 FINISH & ARCHIVE SESSION", use_container_width=True):
            if completed > 0:
                st.session_state.streak += 1
                st.session_state.history.append({
                    "date": get_now_est().strftime('%Y-%m-%d %I:%M %p'),
                    "sport": sport_choice,
                    "drills": completed
                })
                st.balloons()
                st.rerun()
            else:
                st.error("Please log at least one completed drill.")

# --- 7. ARCHIVE ---
else:
    st.title("📊 TRAINING ARCHIVE")
    if not st.session_state.history:
        st.info("No training data recorded yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="background-color:{header_bg}; padding:15px; border-radius:10px; border-left:5px solid {accent}; margin-bottom:10px;">
                <p style="margin:0; font-weight:bold; color:{accent};">{log['date']}</p>
                <p style="margin:0;">{log['sport']} Training - {log['drills']} Drills Logged</p>
            </div>
            """, unsafe_allow_html=True)

st.sidebar.caption("v5.2.1 | ValueError (Rest) Fix")
