import streamlit as st
import pandas as pd
import random
import time
import re
import io
from datetime import datetime
import pytz

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# Initialize persistent session state
if 'streak' not in st.session_state: 
    st.session_state.streak = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

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
        font-family: 'Inter', sans-serif;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important; font-weight: 800 !important;
    }}
    .drill-header {{
        font-size: 24px !important; font-weight: 900 !important; color: {accent} !important;
        background-color: {header_bg}; border-left: 10px solid {accent};
        padding: 15px; border-radius: 0 12px 12px 0; margin-top: 35px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
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
        height: 3em; transition: 0.3s;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CSV DATA ENGINE ---
@st.cache_data
def load_drill_database():
    # Primary URL for basketball.csv
    CSV_URL = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv"
    
    try:
        # Load data and strip whitespace from columns
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        
        # Data Cleaning: Handle Focus Points (Split by semicolon if exists)
        if 'Focus_Points' in df.columns:
            df['Focus_Points'] = df['Focus_Points'].apply(lambda x: x.split(';') if isinstance(x, str) else [])
        else:
            df['Focus_Points'] = [[] for _ in range(len(df))]
            
        return df
    except Exception as e:
        st.sidebar.error(f"CSV Load Error: {e}")
        # Return a structured empty DataFrame to prevent app crash
        return pd.DataFrame(columns=['Sport', 'Exercise', 'Description', 'Base_Sets', 'Base_Goal', 'Unit', 'Rest', 'Location', 'Demo_URL', 'Focus_Points'])

def get_workout_from_csv(df, sport, locs, multiplier):
    if df.empty:
        return []
    
    # Filter by Sport and Location
    mask = (df['Sport'].str.lower() == sport.lower()) & (df['Location'].isin(locs))
    filtered_df = df[mask]
    
    drills = []
    for _, row in filtered_df.iterrows():
        try:
            # Safely handle numeric conversions
            b_sets = float(row.get('Base_Sets', 3))
            b_goal = float(row.get('Base_Goal', 10))
            
            drills.append({
                "ex": row.get('Exercise', 'Unknown Drill'),
                "desc": row.get('Description', 'No description provided.'),
                "sets": b_sets,
                "base": b_goal,
                "unit": row.get('Unit', 'reps'),
                "rest": int(row.get('Rest', 60)),
                "loc": row.get('Location', 'Gym'),
                "demo": row.get('Demo_URL', ''),
                "focus": row.get('Focus_Points', []),
                "scaled_sets": int(round(b_sets * multiplier)),
                "scaled_goal": f"{int(round(b_goal * multiplier))} {row.get('Unit', 'reps')}"
            })
        except Exception:
            continue
    return drills

# --- 4. DATA INITIALIZATION ---
df_drills = load_drill_database()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">EST TIME</p>
        <p style="margin:0; font-size:20px; font-weight:900;">{get_now_est().strftime('%I:%M %p')}</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">STREAK</p>
        <p style="margin:0; font-size:26px; font-weight:900;">{st.session_state.streak} DAYS</p>
    </div>""", unsafe_allow_html=True)

    app_mode = st.selectbox("Navigate System", ["Training Core", "History & Archive", "CSV Manager"])
    
    st.divider()
    
    # Get unique sports from CSV
    available_sports = df_drills['Sport'].unique().tolist() if not df_drills.empty else ["Basketball"]
    sport_choice = st.selectbox("Sport Discipline", available_sports)
    
    st.markdown("### 📍 FACILITY FILTERS")
    
    # FIXED ERROR HERE: Using a list/dict to avoid locals() lookup issues
    loc_checks = {
        "Gym": st.checkbox("Indoor Gym", value=True),
        "Track": st.checkbox("Outdoor Track", value=True),
        "Weight Room": st.checkbox("Weight Room", value=True)
    }
    active_locs = [k for k, v in loc_checks.items() if v]
    
    st.divider()
    
    intensity = st.select_slider("Workout Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    scaling_factor = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[intensity]

# --- 6. CSV MANAGER ---
if app_mode == "CSV Manager":
    st.title("📂 DRILL DATABASE MANAGER")
    st.write(f"Total Drills Indexed: {len(df_drills)}")
    st.dataframe(df_drills, use_container_width=True)
    
    if st.button("Force Database Refresh"):
        st.cache_data.clear()
        st.rerun()

# --- 7. CORE TRAINING ENGINE ---
elif app_mode == "Training Core":
    st.title("PRO-ATHLETE TRACKER")
    st.markdown(f"**Source:** CSV Database | **Intensity:** {intensity}")
    
    session_drills = get_workout_from_csv(df_drills, sport_choice, active_locs, scaling_factor)

    if not session_drills:
        st.warning("⚠️ No drills found in CSV matching your filters. Check Sport and Location columns in your file.")
    else:
        completed_count = 0
        
        for i, item in enumerate(session_drills):
            st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
            
            meta_1, meta_2 = st.columns([3, 1])
            with meta_1:
                st.write(f"**Description:** {item['desc']}")
            with meta_2:
                st.markdown(f"<p style='text-align:right; font-size:12px; color:{accent};'>LOC: {item['loc']}</p>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.text_input("Planned Sets", value=str(item["scaled_sets"]), key=f"s_{i}")
            with c2: 
                st.text_input("Target Goal", value=item['scaled_goal'], key=f"g_{i}")
            with c3: 
                if st.checkbox("Complete", key=f"c_{i}"):
                    completed_count += 1

            st.markdown(f"<p style='color:{electric_blue}; font-weight:900; margin-top:10px;'>ELITE FOCUS POINTS</p>", unsafe_allow_html=True)
            if item["focus"]:
                f_cols = st.columns(len(item["focus"]))
                for idx, pt in enumerate(item["focus"]):
                    with f_cols[idx]:
                        st.markdown(f'<div class="focus-card">🎯 {pt}</div>', unsafe_allow_html=True)
            else:
                st.write("Generic focus: Eye on target, maintain core tension.")

            timer_col, video_col = st.columns([2, 1])
            with timer_col:
                if st.button(f"⏱️ START {item['rest']}s RECOVERY", key=f"r_{i}"):
                    ph = st.empty()
                    for t in range(item['rest'], -1, -1):
                        ph.markdown(f"<h2 style='color:{metric_color};'>Recovery: {t}s</h2>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.empty()
                    st.success("Recovery Complete!")
            
            with video_col:
                with st.expander("🎥 REFERENCE"):
                    if isinstance(item["demo"], str) and "http" in item["demo"]: 
                        st.video(item["demo"])
                    else: 
                        st.info("No video reference available.")

        st.divider()
        st.subheader("Session Summary")
        progress = completed_count / len(session_drills) if session_drills else 0
        st.progress(progress)

        if st.button("🏁 ARCHIVE & FINISH SESSION", use_container_width=True):
            if completed_count > 0:
                st.session_state.streak += 1
                st.session_state.history.append({
                    "date": get_now_est().strftime("%Y-%m-%d %I:%M %p"),
                    "sport": sport_choice,
                    "intensity": intensity,
                    "drills": completed_count
                })
                st.balloons()
                st.success("Session archived!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Log at least one drill to archive.")

# --- 8. HISTORY & ARCHIVE SYSTEM ---
else:
    st.title("📊 ATHLETE ARCHIVE")
    
    if not st.session_state.history:
        st.info("Your training history is currently empty.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Streak", f"{st.session_state.streak} Days", delta="Active")
        m2.metric("Total Sessions", len(st.session_state.history))
        m3.metric("Last Workout", st.session_state.history[-1]['sport'])
        
        st.divider()
        
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="background-color:{header_bg}; padding:20px; border-radius:15px; border-left:8px solid {accent}; margin-bottom:15px;">
                <h3 style="margin:0;">{log['sport']} - {log['intensity']} Level</h3>
                <p style="margin:0; opacity:0.8;">{log['date']}</p>
                <p style="margin-top:10px; font-weight:700;">Performance: {log['drills']} Drills Completed</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ RESET ALL TRACKING DATA"):
            st.session_state.history = []
            st.session_state.streak = 1
            st.rerun()

# --- 9. FOOTER ---
st.sidebar.divider()
st.sidebar.caption("Pro-Athlete Tracker v4.1.2 | Fixed dynamic lookup error")
