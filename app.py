import streamlit as st
import pandas as pd
import random
import time
import re
from datetime import datetime
import pytz

# --- 1. APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="Pro-Athlete Tracker", layout="wide", page_icon="🏆")

# Initialize Session States
if 'history' not in st.session_state:
    st.session_state.history = []
if 'streak' not in st.session_state:
    st.session_state.streak = 1
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'set_counts' not in st.session_state:
    st.session_state.set_counts = {}
if 'workout_finished' not in st.session_state:
    st.session_state.workout_finished = False

def get_now_est():
    return datetime.now(pytz.timezone('US/Eastern'))

# --- 2. DYNAMIC THEMING (SAFARI & HIGH-CONTRAST FIX) ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header, card = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B", "#1E293B"
    electric_blue, sidebar_text = "#00E5FF", "#FFFFFF"
else:
    bg, text, accent, header, card = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9", "#F8FAFC"
    electric_blue, sidebar_text = "#006064", "#111111"

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
    background-color: {header}; border-left: 10px solid {accent};
    padding: 15px; border-radius: 0 12px 12px 0; margin-top: 30px;
}}
.sidebar-card {{ 
    padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
    background-color: {header}; text-align: center; margin-bottom: 15px;
}}
.focus-card {{
    background-color: {header}; padding: 10px; border-radius: 8px;
    border: 1px solid {accent}; margin-bottom: 5px;
}}
.stButton>button {{
    background-color: {accent} !important; color: white !important;
    font-weight: 800 !important; border-radius: 10px !important;
    height: 3em; transition: 0.3s;
}}
</style>
""", unsafe_allow_html=True)

# --- 3. MULTI-DATABASE ENGINE ---
@st.cache_data
def load_all_databases():
    """Loads and merges all CSV files from the repository."""
    base_url = "https://raw.githubusercontent.com/belyeu/sprint-app/refs/heads/main/"
    files = ["basketball.csv", "track.csv", "softball.csv", "general.csv"]
    combined_df = pd.DataFrame()

    for f in files:
        try:
            df = pd.read_csv(base_url + f)
            df.columns = [c.strip() for c in df.columns]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            st.sidebar.warning(f"Note: {f} not found or empty.")
    
    if not combined_df.empty:
        combined_df = combined_df.fillna("N/A")
    return combined_df

def safe_scale(val_str, multiplier):
    """Scales numbers found inside strings (e.g., '10 reps' -> '15 reps')."""
    val_str = str(val_str)
    nums = re.findall(r'\d+', val_str)
    new_str = val_str
    for n in nums:
        scaled = str(int(round(int(n) * multiplier)))
        new_str = new_str.replace(n, scaled, 1)
    return new_str

def get_workout(df, sport, locs, multiplier, limit):
    if df.empty: return []
    
    # Filter by Sport and Location
    mask = (df['Sport'].astype(str).str.strip() == sport) & (df['Location'].isin(locs))
    filtered = df[mask].to_dict('records')
    
    if not filtered: return []
    
    random.shuffle(filtered)
    session = []
    for item in filtered[:limit]:
        # Parse Focus Points if they exist
        fp = item.get('Focus_Points', 'Eyes Up; Core Tight')
        fp_list = fp.split(';') if isinstance(fp, str) else ["Focus"]

        session.append({
            "ex": item.get('Exercise Name', item.get('Exercise', 'Unknown')),
            "desc": item.get('Description', 'N/A'),
            "sets": int(round(pd.to_numeric(item.get('Sets', 3), errors='coerce') * multiplier)),
            "goal": safe_scale(item.get('Reps/Dist', item.get('Reps', '10')), multiplier),
            "rest": int(pd.to_numeric(item.get('Rest', 60), errors='coerce')),
            "demo": str(item.get('Demo', item.get('Demo_URL', ''))).strip(),
            "focus": fp_list
        })
    return session

# --- 4. DATA INITIALIZATION ---
df_master = load_all_databases()

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

    app_mode = st.selectbox("Navigate System", ["Training Core", "History Archive"])
    
    # Identify available sports across ALL CSVs
    if not df_master.empty and 'Sport' in df_master.columns:
        available_sports = sorted(df_master['Sport'].unique().tolist())
    else:
        available_sports = ["Basketball", "Track", "Softball"]
        
    sport_choice = st.selectbox("Sport Discipline", available_sports)
    
    st.markdown("### 📍 LOCATION FILTER")
    l1 = st.checkbox("Gym", value=True)
    l2 = st.checkbox("Track", value=True)
    l3 = st.checkbox("Weight Room", value=True)
    active_locs = [loc for val, loc in zip([l1,l2,l3], ["Gym","Track","Weight Room"]) if val]
    
    num_drills = st.slider("Drill Count", 3, 20, 10)
    intensity = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    scaling_factor = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[intensity]

# --- 6. CORE TRAINING INTERFACE ---
if app_mode == "Training Core":
    st.title("PRO-ATHLETE TRACKER")
    
    if st.button("🚀 GENERATE NEW SESSION", use_container_width=True):
        st.session_state.current_session = get_workout(df_master, sport_choice, active_locs, scaling_factor, num_drills)
        st.session_state.set_counts = {i: 0 for i in range(len(st.session_state.current_session))}
        st.session_state.workout_finished = False

    if st.session_state.current_session and not st.session_state.workout_finished:
        for i, item in enumerate(st.session_state.current_session):
            st.markdown(f'<div class="drill-header">{i+1}. {item["ex"]}</div>', unsafe_allow_html=True)
            st.write(item["desc"])
            
            c1, c2, c3 = st.columns(3)
            with c1: 
                curr = st.session_state.set_counts.get(i, 0)
                if st.button(f"✅ LOG SET ({curr}/{item['sets']})", key=f"log_{i}", use_container_width=True):
                    st.session_state.set_counts[i] += 1
                    st.rerun()
            with c2: 
                st.write(f"**Goal:** {item['goal']}")
            with c3: 
                if st.button(f"⏱️ REST {item['rest']}s", key=f"rest_{i}", use_container_width=True):
                    ph = st.empty()
                    for t in range(item['rest'], -1, -1):
                        ph.markdown(f"<h2 style='text-align:center; color:{accent};'>{t}s</h2>", unsafe_allow_html=True)
                        time.sleep(1)
                    ph.empty()
                    st.success("Go!")

            # Focus Points
            st.markdown(f"<p style='color:{electric_blue}; font-weight:900;'>ELITE FOCUS</p>", unsafe_allow_html=True)
            f_cols = st.columns(len(item["focus"]))
            for idx, pt in enumerate(item["focus"]):
                with f_cols[idx]:
                    st.markdown(f'<div class="focus-card">🎯 {pt.strip()}</div>', unsafe_allow_html=True)

            if "http" in item['demo']:
                with st.expander("🎥 VIDEO REFERENCE"):
                    st.video(item['demo'])

        st.divider()
        if st.button("🏁 ARCHIVE & FINISH SESSION", use_container_width=True):
            st.session_state.history.append({
                "date": get_now_est().strftime("%Y-%m-%d %I:%M %p"),
                "sport": sport_choice,
                "count": len(st.session_state.current_session)
            })
            st.session_state.streak += 1
            st.session_state.workout_finished = True
            st.balloons()
            st.rerun()

# --- 7. HISTORY ARCHIVE ---
else:
    st.title("📊 TRAINING ARCHIVE")
    if not st.session_state.history:
        st.info("No sessions saved. Start training!")
    else:
        for log in reversed(st.session_state.history):
            st.markdown(f"""
            <div style="background-color:{header}; padding:15px; border-radius:10px; border-left:8px solid {accent}; margin-bottom:10px;">
                <h3 style="margin:0;">{log['sport']} Session</h3>
                <p style="margin:0; opacity:0.8;">{log['date']} | {log['count']} Drills Completed</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Clear Archive"):
            st.session_state.history = []
            st.rerun()

st.sidebar.caption("v6.0.0 | Multi-CSV Integrated")
