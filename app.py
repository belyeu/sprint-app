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
if 'last_summary' not in st.session_state:
    st.session_state.last_summary = None

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEME (HIGH CONTRAST & SAFARI FIX) ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue, sidebar_text, card_bg = "#00E5FF", "#FFFFFF", "#1E293B"
    metric_color = "#38BDF8"
    success_bg = "#064E3B"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue, sidebar_text, card_bg = "#006064", "#111111", "#F8FAFC"
    metric_color = "#1E40AF"
    success_bg = "#D1FAE5"

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
    }}
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
        background-color: {card_bg}; text-align: center; margin-bottom: 15px;
    }}
    .focus-card {{
        background-color: {header_bg}; padding: 10px; border-radius: 8px;
        border: 1px solid {accent}; margin-bottom: 5px;
    }}
    .summary-box {{
        background-color: {header_bg}; padding: 30px; border-radius: 15px;
        border: 2px solid {electric_blue}; text-align: center; margin-bottom: 20px;
    }}
    .stButton>button {{
        background-color: {accent} !important; color: white !important;
        font-weight: 800 !important; border-radius: 10px !important;
        height: 3em;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CSV DATA ENGINE ---
@st.cache_data
def load_drills_from_csv():
    # Define your CSV sources
    csv_files = {
        "Basketball": "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/basketball.csv",
        # "Soccer": "..." (Add more here)
    }
    
    all_drills = []
    
    for sport_name, url in csv_files.items():
        try:
            df = pd.read_csv(url)
            df.columns = [c.strip() for c in df.columns]
            
            for _, row in df.iterrows():
                focus = row.get('Focus_Points', '')
                focus_list = focus.split(';') if isinstance(focus, str) else []
                
                drill_data = {
                    "Sport": sport_name,
                    # Added 'Type' column extraction (defaults to 'General' if missing)
                    "Type": row.get('Type', row.get('Category', 'General')), 
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

def get_workout(df, sport, locs, types, multiplier):
    if df.empty: return []
    
    # Filter by Sport, Location, AND Type
    mask = (df['Sport'] == sport) & (df['Location'].isin(locs)) & (df['Type'].isin(types))
    filtered = df[mask]
    
    drills = []
    for _, row in filtered.iterrows():
        raw_goal = str(row['Base_Goal'])
        nums = re.findall(r'\d+', raw_goal)
        scaled_goal = raw_goal
        for n in nums:
            scaled_val = str(int(round(int(n) * multiplier)))
            scaled_goal = scaled_goal.replace(n, scaled_val, 1)

        drills.append({
            "ex": row['Exercise'],
            "type": row['Type'],
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

    app_mode = st.selectbox("Navigate", ["Training Core", "History Archive"])
    
    # 1. Sport Selection
    available_sports = df_master['Sport'].unique().tolist() if not df_master.empty else ["Basketball"]
    sport_choice = st.selectbox("Select Sport", available_sports)
    
    # 2. Location Filter
    st.markdown("### 📍 FACILITY")
    loc_checks = {
        "Gym": st.checkbox("Gym", value=True),
        "Track": st.checkbox("Track", value=True),
        "Weight Room": st.checkbox("Weight Room", value=True)
    }
    active_locs = [k for k, v in loc_checks.items() if v]

    # 3. NEW: Type Filter (Dynamic based on Sport)
    st.markdown("### 🏷️ DRILL TYPES")
    if not df_master.empty:
        # Get unique types for the selected sport
        sport_types = df_master[df_master['Sport'] == sport_choice]['Type'].unique().tolist()
        # Default to selecting all available types
        selected_types = st.multiselect("Filter by Category", sport_types, default=sport_types)
    else:
        selected_types = ["General"]

    st.divider()
    intensity = st.select_slider("Intensity", options=["Standard", "Elite", "Pro"], value="Elite")
    scaling_factor = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[intensity]

# --- 6. MAIN INTERFACE ---
if st.session_state.workout_finished:
    # === SESSION SUMMARY PAGE ===
    st.title("🏆 SESSION COMPLETE")
    
    summary = st.session_state.last_summary
    
    # Hero Card
    st.markdown(f"""
    <div class="summary-box">
        <h2 style="color:{metric_color}; margin:0;">WORKOUT CRUSHED</h2>
        <p style="font-size:18px;">{summary['date']}</p>
        <hr style="border-color:{accent};">
        <div style="display:flex; justify-content:space-around;">
            <div>
                <h1>{summary['drills']}</h1>
                <p>Drills Completed</p>
            </div>
            <div>
                <h1>{summary['intensity']}</h1>
                <p>Intensity Level</p>
            </div>
            <div>
                <h1>{st.session_state.streak}</h1>
                <p>Day Streak</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⬅️ START NEW WORKOUT", use_container_width=True):
        st.session_state.workout_finished = False
        st.rerun()

elif app_mode == "Training Core":
    st.title("PRO-ATHLETE TRACKER")
    
    # Pass selected_types to the function
    session_drills = get_workout(df_master, sport_choice, active_locs, selected_types, scaling_factor)

    if not session_drills:
        st.warning(f"No drills found. Check filters for {sport_choice} in {active_locs} with types {selected_types}.")
    else:
        completed = 0
        total_drills = len(session_drills)
        
        # Global Progress Bar
        st.progress(0, text=f"Session Progress: 0/{total_drills}")

        for i, item in enumerate(session_drills):
            st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]} <span style="font-size:14px; opacity:0.7;">({item["type"]})</span></div>', unsafe_allow_html=True)
            
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

            # === UPGRADED STOPWATCH TIMER ===
            t_col, v_col = st.columns([2, 1])
            with t_col:
                # Unique key for every drill's timer button
                if st.button(f"⏱️ RECOVERY ({item['rest']}s)", key=f"r_{i}"):
                    timer_placeholder = st.empty()
                    bar_placeholder = st.empty()
                    
                    total_time = item['rest']
                    for t in range(total_time, -1, -1):
                        # Calculate percentage for progress bar
                        prog = 1.0 - (t / total_time)
                        # Ensure prog is within 0.0 to 1.0
                        prog = max(0.0, min(1.0, prog))
                        
                        timer_placeholder.markdown(f"<h1 style='color:{metric_color}; text-align:center; font-size:40px;'>{t}s</h1>", unsafe_allow_html=True)
                        bar_placeholder.progress(prog)
                        time.sleep(1)
                    
                    timer_placeholder.markdown(f"<h2 style='color:#10B981; text-align:center;'>GO!</h2>", unsafe_allow_html=True)
                    bar_placeholder.empty()

            with v_col:
                with st.expander("🎥 VIDEO"):
                    if "http" in str(item["demo"]): st.video(item["demo"])
                    else: st.info("No video.")

        st.divider()
        
        # Summary Button Logic
        if st.button("🏁 FINISH & VIEW SUMMARY", use_container_width=True):
            if completed > 0:
                st.session_state.streak += 1
                
                summary_data = {
                    "date": get_now_est().strftime("%B %d, %Y - %I:%M %p"),
                    "sport": sport_choice,
                    "intensity": intensity,
                    "drills": completed
                }
                
                st.session_state.history.append(summary_data)
                st.session_state.last_summary = summary_data
                st.session_state.workout_finished = True # Trigger the summary page
                st.balloons()
                st.rerun()
            else:
                st.error("Complete at least one drill to finish.")

else:
    # HISTORY PAGE
    st.title("📊 ARCHIVE")
    if not st.session_state.history:
        st.info("No history yet.")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""<div style="background-color:{header_bg}; padding:15px; border-radius:10px; border-left:5px solid {accent}; margin-bottom:10px;">
                <strong>{log['date']}</strong><br>
                {log['sport']} ({log['intensity']}) - {log['drills']} Drills
                </div>""", unsafe_allow_html=True)

st.sidebar.caption("v5.1.0 | Type Filters & Summary")
