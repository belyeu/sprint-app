import streamlit as st
import pandas as pd
import random
import time
import re
import os
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

# --- 3. CSV DATA ENGINE (FIXED FOR FILENAME-BASED SPORT) ---
@st.cache_data
def load_drills_from_csv():
    # List of CSV files in your repository
    # Since the sport name IS the filename, we map them here:
    csv_files = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
        # Add other sports here as you upload them, e.g.:
        # "Soccer": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/soccer.csv"
    }
    
    all_drills = []
    
    for sport_name, url in csv_files.items():
        try:
            df = pd.read_csv(url)
            df.columns = [c.strip() for c in df.columns]
            
            # Map columns and inject the sport name from the filename/key
            for _, row in df.iterrows():
                # Handling focus points which might be semicolon separated
                focus = row.get('Focus_Points', '')
                focus_list = focus.split(';') if isinstance(focus, str) else []
                
                drill_data = {
                    "Sport": sport_name, # Derived from filename
                    "Exercise": row.get('Exercise Name', row.get('Exercise', 'Unknown')),
                    "Description": row.get('Description', 'N/A'),
                    "Base_Sets": row.get('Sets', 3),
                    "Base_Goal": row.get('Reps/Dist', row.get('Reps', 10)),
                    "Unit": row.get('Unit', ''),
                    "Rest": row.get('Rest', 60),
                    "Location": row.get('Location', 'Gym'),
                    "Demo_URL": row.get('Demo', row.get('Demo_URL', '')),
                    "Focus_Points": focus_list
                }
                all_drills.append(drill_data)
        except Exception as e:
            st.sidebar.warning(f"Could not load {sport_name}: {e}")
            
    return pd.DataFrame(all_drills)

def get_workout(df, sport, locs, multiplier):
    if df.empty: return []
    
    mask = (df['Sport'] == sport) & (df['Location'].isin(locs))
    filtered = df[mask]
    
    drills = []
    for _, row in filtered.iterrows():
        # Scaling logic for numeric values within Reps/Dist strings
        raw_goal = str(row['Base_Goal'])
        nums = re.findall(r'\d+', raw_goal)
        scaled_goal = raw_goal
        for n in nums:
            scaled_val = str(int(round(int(n) * multiplier)))
            scaled_goal = scaled_goal.replace(n, scaled_val, 1)

        drills.append({
            "ex": row['Exercise'],
            "desc": row['Description'],
            "sets": int(round(int(row['Base_Sets']) * multiplier)),
            "goal": scaled_goal,
            "unit": row['Unit'],
            "rest": int(row['Rest']),
            "loc": row['Location'],
            "demo": row['Demo_URL'],
            "focus": row['Focus_Points']
        })
    return drills

# --- 4. INITIALIZE DATA ---
df_master = load_drills_from_csv()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">EST TIME</p>
        <p style="margin:0; font-size:20px; font-weight:900;">{get_now_est().strftime('%I:%M %p')}</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">STREAK</p>
        <p style="margin:0; font-size:26px; font-weight:900;">{st.session_state.streak} DAYS</p>
    </div>""", unsafe_allow_html=True)

    app_mode = st.selectbox("Navigate", ["Training Core", "History Archive"])
    
    # Dynamic sport selection based on loaded files
    available_sports = df_master['Sport'].unique().tolist() if not df_master.empty else ["Basketball"]
    sport_choice = st.selectbox("Select Sport", available_sports)
    
    st.markdown("### 📍 FACILITY")
    loc_checks = {
        "Gym": st.checkbox("Gym", value=True),
        "Track": st.checkbox("Track", value=True),
        "Weight Room": st.checkbox("Weight Room", value=True)
    }
    active_locs = [k for k, v in loc_checks.items() if v]
    
    intensity = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    scaling_factor = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[intensity]

# --- 6. MAIN INTERFACE ---
if app_mode == "Training Core":
    st.title("PRO-ATHLETE TRACKER")
    
    session_drills = get_workout(df_master, sport_choice, active_locs, scaling_factor)

    if not session_drills:
        st.warning("No drills found. Check your CSV column names (Exercise, Sets, Reps/Dist, Location).")
    else:
        completed = 0
        for i, item in enumerate(session_drills):
            st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
            
            st.write(f"**Description:** {item['desc']}")
            
            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("Sets", value=str(item["sets"]), key=f"s_{i}")
            with c2: st.text_input("Goal", value=item['goal'], key=f"g_{i}")
            with c3: 
                if st.checkbox("Done", key=f"c_{i}"): completed += 1

            if item["focus"]:
                st.markdown(f"<p style='color:{electric_blue}; font-weight:900;'>FOCUS</p>", unsafe_allow_html=True)
                f_cols = st.columns(len(item["focus"]))
                for idx, pt in enumerate(item["focus"]):
                    with f_cols[idx]: st.markdown(f'<div class="focus-card">🎯 {pt}</div>', unsafe_allow_html=True)

            t_col, v_col = st.columns([2, 1])
            with t_col:
                if st.button(f"⏱️ RECOVERY ({item['rest']}s)", key=f"r_{i}"):
                    ph = st.empty()
                    for t in range(item['rest'], -1, -1):
                        ph.markdown(f"<h2 style='color:{metric_color};'>Rest: {t}s</h2>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.empty()
            with v_col:
                with st.expander("🎥 VIDEO"):
                    if "http" in str(item["demo"]): st.video(item["demo"])
                    else: st.info("No video.")

        st.divider()
        if st.button("🏁 ARCHIVE SESSION", use_container_width=True):
            if completed > 0:
                st.session_state.streak += 1
                st.session_state.history.append({"date": get_now_est().strftime("%Y-%m-%d"), "sport": sport_choice, "drills": completed})
                st.balloons()
                st.rerun()
            else:
                st.error("Complete at least one drill.")

else:
    st.title("📊 ARCHIVE")
    if not st.session_state.history:
        st.info("No history yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""<div style="background-color:{header_bg}; padding:15px; border-radius:10px; border-left:5px solid {accent}; margin-bottom:10px;">
                <strong>{log['date']}</strong>: {log['sport']} - {log['drills']} Drills Completed</div>""", unsafe_allow_html=True)

st.sidebar.caption("v5.0.0 | Filename-based Sport Mapping")
