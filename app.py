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

# --- 2. DYNAMIC THEME & CSS ---
st.sidebar.markdown("### 🌓 DISPLAY SETTINGS")
dark_mode = st.sidebar.toggle("Dark Mode", value=True)

if dark_mode:
    bg, text, accent, header_bg = "#0F172A", "#FFFFFF", "#3B82F6", "#1E293B"
    electric_blue, sidebar_text = "#00E5FF", "#FFFFFF"
else:
    bg, text, accent, header_bg = "#FFFFFF", "#000000", "#1E40AF", "#F1F5F9"
    electric_blue, sidebar_text = "#006064", "#111111"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    h1, h2, h3, p, span, li {{ color: {text} !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
        font-weight: 800 !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {electric_blue} !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }}
    .drill-header {{
        font-size: 22px !important; font-weight: 900 !important; color: {accent} !important;
        background-color: {header_bg}; border-left: 8px solid {accent};
        padding: 10px; border-radius: 0 10px 10px 0; margin-top: 20px;
    }}
    .sidebar-card {{ 
        padding: 15px; border-radius: 12px; border: 3px solid {accent}; 
        background-color: {header_bg}; text-align: center; margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE MASTER DATABASE ---
def get_workout_template(sport, locs, active_categories=None):
    if sport == "Basketball":
        all_bb_drills = [
            {"cat": "Warm-up", "ex": "High/Low Walking (Right)", "desc": "3 High, 3 Low; keep chest up.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Chest Up", "Hand Speed"]},
            {"cat": "Warm-up", "ex": "High/Low Walking (Left)", "desc": "Focus on the weak hand.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Weak Hand", "Control"]},
            {"cat": "Warm-up", "ex": "High/Low Backpedal (Right)", "desc": "Three high, three low moving backward.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Balance", "Rhythm"]},
            {"cat": "Warm-up", "ex": "High/Low Backpedal (Left)", "desc": "Maintaining balance while retreating.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Coordination", "Retreat"]},
            {"cat": "Warm-up", "ex": "Forward Skip (Right)", "desc": "Ball by the hip.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Hip Pocket", "Rhythm"]},
            {"cat": "Warm-up", "ex": "Forward Skip (Left)", "desc": "Full court length.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Weak Hand", "Extension"]},
            {"cat": "Warm-up", "ex": "Backward Skip (Right)", "desc": "Maintaining pace and height.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Pace", "Coordination"]},
            {"cat": "Warm-up", "ex": "Backward Skip (Left)", "desc": "Focus on coordination.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Coordination", "Height"]},
            {"cat": "Warm-up", "ex": "Side Shuffle (Right Hand)", "desc": "Facing one direction.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Lateral Speed", "Hand Depth"]},
            {"cat": "Warm-up", "ex": "Side Shuffle (Left Hand)", "desc": "Facing the opposite direction.", "base": 1, "unit": "Length", "loc": "Gym", "focus": ["Opposite View", "Low Stance"]},
            {"cat": "Crossover", "ex": "Stationary High", "desc": "Dribble at waist/chest height.", "base": 50, "unit": "reps", "loc": "Gym", "focus": ["Power", "Shoulder Sway"]},
            {"cat": "Crossover", "ex": "Stationary Medium", "desc": "Dribble at knee height.", "base": 50, "unit": "reps", "loc": "Gym", "focus": ["Knee Level", "Rhythm"]},
            {"cat": "Crossover", "ex": "Stationary Low", "desc": "Rapid ankle-height dribbles.", "base": 50, "unit": "reps", "loc": "Gym", "focus": ["Fingertips", "Speed"]},
            {"cat": "Crossover", "ex": "Pocket Pull", "desc": "Pulling the ball back to protect from reach.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Protection", "Wrist Snap"]},
            {"cat": "Crossover", "ex": "Cross Step Jab", "desc": "Jabbing at the defense during the cross.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Deception", "Footwork"]},
            {"cat": "Crossover", "ex": "Continuous Shuffle", "desc": "Moving feet rhythmically during crossovers.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Foot Speed", "Coordination"]},
            {"cat": "Crossover", "ex": "Push Crossover (Right)", "desc": "Pushing the ball over the top forward.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Forward Push", "Shoulder Low"]},
            {"cat": "Crossover", "ex": "Push Crossover (Left)", "desc": "Moving toward the baseline.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Baseline Drive", "Control"]},
            {"cat": "Crossover", "ex": "Allen Iverson Step", "desc": "Wide deceptive step-across.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Wide Step", "Head Fake"]},
            {"cat": "Crossover", "ex": "Trae Young Pullback", "desc": "Lunging and snapping back for space.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Separation", "Lunge Speed"]},
            {"cat": "Crossover", "ex": "Double Tap", "desc": "Dropping and tapping twice before the cross.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Change of Pace", "Double Rhythm"]},
            {"cat": "Crossover", "ex": "V-Dribble (Right)", "desc": "One-handed crossover shape.", "base": 30, "unit": "reps", "loc": "Gym", "focus": ["One Hand", "Wide Arc"]},
            {"cat": "Crossover", "ex": "V-Dribble (Left)", "desc": "Using a jab to sell the move.", "base": 30, "unit": "reps", "loc": "Gym", "focus": ["Weak Hand", "Jab Step"]},
            {"cat": "Crossover", "ex": "Shammgod", "desc": "Pushing out with one hand, pulling back with the other.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Extension", "Recovery"]},
            {"cat": "Combos", "ex": "Pound Cross", "desc": "Adding a power dribble before the cross.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Pound Power", "Fast Cross"]},
            {"cat": "Combos", "ex": "Between-Cross-Front", "desc": "Triple move sequence.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Flow", "Rhythm"]},
            {"cat": "Combos", "ex": "Pound-Between", "desc": "Power dribble into between the legs.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Hard Dribble", "Clean Leg Flow"]},
            {"cat": "Combos", "ex": "Inside Out-Cross", "desc": "Faking one way, crossing the other.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Shoulder Fake", "Eyes"]},
            {"cat": "Between Legs", "ex": "Stationary (No Feet)", "desc": "Keeping feet planted.", "base": 30, "unit": "reps", "loc": "Gym", "focus": ["Low Stance", "Hand Speed"]},
            {"cat": "Between Legs", "ex": "Continuous", "desc": "Rapid-fire without extra dribbles.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["No Extra Dribbles", "Flow"]},
            {"cat": "Between Legs", "ex": "Boxer/Shuffle Feet", "desc": "Moving feet while dribbling through.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Foot Twitch", "Rhythm"]},
            {"cat": "Between Legs", "ex": "Forward Lunge", "desc": "Stepping toward the defender.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Attack Angle", "Lunge"]},
            {"cat": "Between Legs", "ex": "Side Jab", "desc": "Shifting defense laterally.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Lateral Shift", "Hard Jab"]},
            {"cat": "Between Legs", "ex": "Walking Backwards", "desc": "Dribbling through while retreating.", "base": 2, "unit": "Length", "loc": "Gym", "focus": ["Retreat Speed", "Coordination"]},
            {"cat": "Between Legs", "ex": "Outside-In (Reverse)", "desc": "Dribbling from the outside of the leg in.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Inverted Flow", "Control"]},
            {"cat": "On the Move", "ex": "Inside Out (Right)", "desc": "Exaggerating eyes and shoulders.", "base": 2, "unit": "Length", "loc": "Gym", "focus": ["Eye Fake", "Hard Dribble"]},
            {"cat": "On the Move", "ex": "Inside Out (Left)", "desc": "Full court repetition.", "base": 2, "unit": "Length", "loc": "Gym", "focus": ["Weak Hand", "Extension"]},
            {"cat": "On the Move", "ex": "Retreat Inside Out", "desc": "Beating pressure then attacking.", "base": 2, "unit": "Length", "loc": "Gym", "focus": ["Change of Speed", "Attack"]},
            {"cat": "On the Move", "ex": "Under Leg Stop", "desc": "Creating separation on the drive.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Sudden Stop", "Separation"]},
            {"cat": "Behind Back", "ex": "Sharp Behind", "desc": "Dribbling under the glutes.", "base": 30, "unit": "reps", "loc": "Gym", "focus": ["Tight Path", "Under Glutes"]},
            {"cat": "Behind Back", "ex": "Wrap Behind", "desc": "Circular motion around the waist.", "base": 30, "unit": "reps", "loc": "Gym", "focus": ["Extension", "Wrist Wrap"]},
            {"cat": "Fakes", "ex": "Side/Float Dribble", "desc": "Simulating a shot to freeze the defense.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Freeze Defender", "Eyes up"]},
            {"cat": "Fakes", "ex": "Rip & Drive (Right)", "desc": "Extending the ball far away from the body.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Extension", "Hard Drive"]},
            {"cat": "Fakes", "ex": "Rip & Drive (Left)", "desc": "Triple threat explosion.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Explosive First Step", "Low Shoulder"]},
            {"cat": "Post-Up", "ex": "Spin into Post-up", "desc": "Protecting the ball while turning your back.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Ball Protection", "Pivot"]},
            {"cat": "Transition", "ex": "Stutter Step", "desc": "Chopping feet to change speeds.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Fast Feet", "Speed Change"]},
            {"cat": "Transition", "ex": "Delayed Between Legs", "desc": "Falling asleep move then exploding.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Lull Defender", "Burst"]},
            {"cat": "Slide Series", "ex": "Slide & Drive", "desc": "Shifting the defender to open a gap.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Gap Recognition", "Shoulder dip"]},
            {"cat": "Slide Series", "ex": "Slide-Crossover", "desc": "Lateral move into a change of direction.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Lateral to Linear", "Cross Speed"]},
            {"cat": "Slide Series", "ex": "Slide-Between Legs", "desc": "Maintaining spacing outside the perimeter.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Spacing", "Perimeter Move"]},
            {"cat": "Slide Series", "ex": "Behind-Slide-Behind", "desc": "Advanced coordination sequence.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Fluidity", "Footwork"]},
            {"cat": "Slide Series", "ex": "Slide-Inside Out", "desc": "Faking the drive out of a float.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Float Fake", "Hesitation"]},
            {"cat": "Slide Series", "ex": "Slide-Double Move", "desc": "Custom combo (e.g., cross-cross).", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Quick Hands", "Counter Move"]},
            {"cat": "Float Series", "ex": "Between Legs Float", "desc": "Letting the ball float in the hand.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Ball Hang Time", "Feet Ready"]},
            {"cat": "Float Series", "ex": "Behind Back Float", "desc": "Changing speeds out of the float.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Speed Burst", "Float Control"]},
            {"cat": "Jabs", "ex": "Opposite Foot Jab", "desc": "Stepping across the defender's frame.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Step Across", "Shoulder Fake"]},
            {"cat": "Jabs", "ex": "Same Foot/Same Hand", "desc": "Threatening the drive to force a retreat.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Same Side", "Force Retreat"]},
            {"cat": "Jabs", "ex": "Side Jab (Opposite Foot)", "desc": "Forcing the defender to shift laterally.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Lateral Shift", "Hard Jab"]},
            {"cat": "Jabs", "ex": "Cross-Opposite Jab", "desc": "Combining a crossover with a foot jab.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Combined Move", "Rhythm"]},
            {"cat": "Jabs", "ex": "Between-Opposite Jab", "desc": "Adding a leg through move to the jab.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Leg Flow", "Jab Speed"]},
            {"cat": "Jabs", "ex": "Behind-Opposite Jab", "desc": "Creating space out of the back dribble.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Space Creation", "Back Dribble"]},
            {"cat": "Jabs", "ex": "Inside Out Jab", "desc": "Forward step vs. side step variations.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Inside Out", "Jab Variation"]},
            {"cat": "Stop Series", "ex": "Same Foot/Hand Stop", "desc": "Immediate emergency stop to shoot.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Sudden Stop", "Balance"]},
            {"cat": "Stop Series", "ex": "Opposite Foot/Hand Stop", "desc": "Stopping on the dime to create space.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Dime Stop", "Shoulder Square"]},
            {"cat": "Stop Series", "ex": "Behind the Back Stop", "desc": "Sprinting into a behind the back halt.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Sprint Control", "Behind Stop"]},
            {"cat": "Stop Series", "ex": "Under Leg Stop", "desc": "Inside-to-outside stop.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Inside Out Stop", "Pivot"]},
            {"cat": "Stop Series", "ex": "Half Turn Stop", "desc": "Jabbing across the body to halt.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Jab Cross", "Halt"]},
            {"cat": "Retreats", "ex": "Hip Swivel", "desc": "Squaring up from a back-down position.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Hip Speed", "Square Up"]},
            {"cat": "Retreats", "ex": "Sprint Back (Left Pivot)", "desc": "One big dribble back to relieve pressure.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Relieve Pressure", "Big Step"]},
            {"cat": "Retreats", "ex": "Sprint Back (Right Pivot)", "desc": "Creating space for a shot or drive.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Pivot Power", "Space"]},
            {"cat": "Retreats", "ex": "Ball Screen Retreat", "desc": "Escaping a hedge defender.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Escape Hedge", "Eyes Up"]},
            {"cat": "Retreats", "ex": "Double Move Retreat", "desc": "Recovering after a defender cuts you off.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Recovery", "Double Move"]},
            {"cat": "Retreats", "ex": "Drive & Relocate", "desc": "Retreating to the corner/wing after a drive.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Relocation", "Drive Speed"]},
            {"cat": "Twitchy", "ex": "Shoulder Rock Walking", "desc": "Exaggerating movement to be deceptive.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Deception", "Shoulder Rock"]},
            {"cat": "Twitchy", "ex": "Slide-Twitch", "desc": "Adding a slide to the rocking motion.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Lateral Twitch", "Balance"]},
            {"cat": "Twitchy", "ex": "Between-Cross Twitch", "desc": "Rapid-fire change of direction.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Fast Direction Change", "Twitch"]},
            {"cat": "Drop Series", "ex": "Drop-Between Legs", "desc": "Shoulders to hips of the defender.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Hip Level", "Drop Step"]},
            {"cat": "Drop Series", "ex": "Drop-Crossover", "desc": "Getting the shoulder through the gap.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Gap Attack", "Shoulder Low"]},
            {"cat": "Drop Series", "ex": "Push Out Cross", "desc": "Driving from a low, split position.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Split Position", "Push Out"]},
            {"cat": "Spins", "ex": "Basic Driving Spin", "desc": "Spinning when a defender overplays.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Spin Speed", "Ball Placement"]},
            {"cat": "Spins", "ex": "Baseline Spin", "desc": "Using pressure to roll to the rim.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Baseline Use", "Rim Finish"]},
            {"cat": "Spins", "ex": "Crossover-Spin", "desc": "Linking the cross and the turn.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Linked Combo", "Footwork"]},
            {"cat": "Spins", "ex": "Between Legs-Spin", "desc": "Using the leg move as the setup.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Leg Setup", "Turn Speed"]},
            {"cat": "Spins", "ex": "Behind Back-Spin", "desc": "Tight, straight-line turn.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Straight Line", "Tight Turn"]},
            {"cat": "Spins", "ex": "Half-Spin (Deceptive)", "desc": "Faking the turn and looking back.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Fake Turn", "Head Look"]},
            {"cat": "Spins", "ex": "Double Move Half-Spin", "desc": "Combo move into the fake spin.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Double Fake", "Half Spin Flow"]},
            {"cat": "Stationary", "ex": "4 Sets of 2 (V-Dribble)", "desc": "Two reps of each move in sequence.", "base": 8, "unit": "reps", "loc": "Gym", "focus": ["Rhythm", "V-Shape"]},
            {"cat": "Stationary", "ex": "4 Sets of 2 (Cross)", "desc": "Building rhythmic speed.", "base": 8, "unit": "reps", "loc": "Gym", "focus": ["Cross Rhythm", "Speed"]},
            {"cat": "Stationary", "ex": "4 Sets of 2 (In & Out)", "desc": "Part of the Power 4 drill.", "base": 8, "unit": "reps", "loc": "Gym", "focus": ["In & Out", "Power"]},
            {"cat": "Stationary", "ex": "4 Sets of 2 (Behind)", "desc": "Final piece of the sequence.", "base": 8, "unit": "reps", "loc": "Gym", "focus": ["Behind Finish", "Flow"]},
            {"cat": "Stationary", "ex": "Front Extension", "desc": "Reaching the ball out as far as possible.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Extension", "Reach"]},
            {"cat": "Stationary", "ex": "Side Extension", "desc": "Maintaining 50/50 balance while reaching.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Side Reach", "Balance"]},
            {"cat": "Stationary", "ex": "Over the Knee", "desc": "Dribbling from center to outside the knee.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Knee Arc", "Hand Speed"]},
            {"cat": "Stationary", "ex": "Side Up & Back", "desc": "Pushing the ball fast on the lateral line.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Lateral Line", "Speed Push"]},
            {"cat": "Stationary", "ex": "Around Leg Circle", "desc": "Dribbling across the body and behind.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Circular Path", "Behind Leg"]},
            {"cat": "Stationary", "ex": "High to Low Speeds", "desc": "Changing heights and tempos.", "base": 45, "unit": "sec", "loc": "Gym", "focus": ["Speed Change", "Height Change"]},
            {"cat": "Contact", "ex": "Shoulder Pressure", "desc": "Crossover while being pushed.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Core Stability", "Resistance"]},
            {"cat": "Contact", "ex": "Wrist/Forearm Hitting", "desc": "Dribbling through defensive hacks.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Grip Strength", "Focus"]},
            {"cat": "Contact", "ex": "Side Lunge Pressure", "desc": "Resisting movement from the side.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Side Balance", "Lunge Resistance"]},
            {"cat": "Contact", "ex": "Back/Hip Grabbing", "desc": "Staying balanced with rear-end contact.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Balance", "Hip Resilience"]},
            {"cat": "Contact", "ex": "Drive Through", "desc": "Football-style straight-line resistance.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Shoulder Low", "Drive Power"]},
            {"cat": "Contact", "ex": "Zig-Zag Dribbling", "desc": "Both offense and defense dribble.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Defense Mirror", "Zig-Zag Flow"]},
            {"cat": "2-Ball", "ex": "Rhythm Pass", "desc": "Chest passes while keeping rhythm alive.", "base": 20, "unit": "reps", "loc": "Gym", "focus": ["Pass Accuracy", "Rhythm"]},
            {"cat": "2-Ball", "ex": "Machine Gun Pass", "desc": "Alternating dribbles into a pass.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Alternating Flow", "Sharp Pass"]},
            {"cat": "2-Ball", "ex": "Side Partner Pass", "desc": "Passing across the body.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Side Pass", "Coordination"]},
            {"cat": "2-Ball", "ex": "Behind the Back Pass", "desc": "Advanced coordination with a partner.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Advanced Flow", "Behind Pass"]},
            {"cat": "2-Ball", "ex": "Two-Ball Skip", "desc": "Rhythm and machine gun variations.", "base": 2, "unit": "Laps", "loc": "Gym", "focus": ["Skip Rhythm", "Two-Ball Control"]},
            {"cat": "2-Ball", "ex": "Mixed Extension", "desc": "One ball front, one ball side.", "base": 30, "unit": "sec", "loc": "Gym", "focus": ["Dual Focus", "Extension Range"]},
            {"cat": "Tennis Ball", "ex": "Spike-Cross-Catch", "desc": "Using the tennis ball to force ball control.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Hand-Eye", "Cross Speed"]},
        ]
        filtered = [d for d in all_bb_drills if d['loc'] in locs]
        if active_categories:
            filtered = [d for d in filtered if d['cat'] in active_categories]
        return filtered

    elif sport == "Softball":
        softball_drills = [
            {"cat": "Hitting", "ex": "TEE WORK", "desc": "Refinement and path.", "base": 25, "unit": "swings", "loc": "Batting Cages", "focus": ["Path", "Hip Drive"]},
            {"cat": "Fielding", "ex": "GLOVE TRANSFERS", "desc": "Transfer speed drill.", "base": 30, "unit": "reps", "loc": "Softball Field", "focus": ["Quick Release", "Grip"]},
            {"cat": "Hitting", "ex": "INSIDE PITCH PULLS", "desc": "Hands on inside pitches.", "base": 15, "unit": "swings", "loc": "Batting Cages", "focus": ["Hands First", "Finish"]},
            {"cat": "Fielding", "ex": "PICKER HOPS", "desc": "Fielding velocity decision.", "base": 20, "unit": "reps", "loc": "Softball Field", "focus": ["Glove Down", "Balance"]},
            {"cat": "Arm", "ex": "LONG TOSS", "desc": "Arm strength and distance.", "base": 15, "unit": "throws", "loc": "Softball Field", "focus": ["Arc", "Follow Through"]},
            {"cat": "Hitting", "ex": "TWO-BALL FOCUS", "desc": "Vision for selective hitting.", "base": 10, "unit": "swings", "loc": "Batting Cages", "focus": ["Vision", "Reaction"]},
            {"cat": "Speed", "ex": "SPRINT TO FIRST", "desc": "Max speed burst.", "base": 6, "unit": "sprints", "loc": "Softball Field", "focus": ["Burst", "Finish"]},
            {"cat": "Hitting", "ex": "BUNTING DRILLS", "desc": "Precision bat control.", "base": 10, "unit": "bunts", "loc": "Batting Cages", "focus": ["Bat Angle", "Pivot"]}
        ]
        return [d for d in softball_drills if d['loc'] in locs]

    elif sport == "Track":
        track_drills = [
            {"cat": "Technique", "ex": "A-SKIPS", "desc": "Rhythmic knee drive mechanics.", "base": 40, "unit": "meters", "loc": "Track", "focus": ["Knee Drive", "Toe Up"]},
            {"cat": "Power", "ex": "BOUNDING", "desc": "Horizontal power and air time.", "base": 30, "unit": "meters", "loc": "Track", "focus": ["Extension", "Elastic Force"]},
            {"cat": "Speed", "ex": "HILL SPRINTS", "desc": "Explosive force against gravity.", "base": 6, "unit": "reps", "loc": "Track", "focus": ["Forward Lean", "Intensity"]},
            {"cat": "Technique", "ex": "ANKLE DRIBBLES", "desc": "Low-amplitude turnover speed.", "base": 20, "unit": "meters", "loc": "Track", "focus": ["Dorsiflexion", "Rapid Touch"]},
            {"cat": "Stability", "ex": "SINGLE LEG HOPS", "desc": "Reactive power and stability.", "base": 10, "unit": "reps", "loc": "Track", "focus": ["Stiff Ankle", "Control"]},
            {"cat": "Speed", "ex": "ACCELERATIONS", "desc": "Phase-specific speed building.", "base": 30, "unit": "meters", "loc": "Track", "focus": ["Push Phase", "Drive"]},
            {"cat": "Technique", "ex": "WALL DRILLS", "desc": "Isolating sprint posture.", "base": 20, "unit": "switches", "loc": "Track", "focus": ["Hip Snap", "Core Strength"]},
            {"cat": "Endurance", "ex": "800M FINISHER", "desc": "Anaerobic capacity builder.", "base": 800, "unit": "meters", "loc": "Track", "focus": ["Kick", "Breathing"]}
        ]
        return [d for d in track_drills if d['loc'] in locs]

    elif sport == "General":
        general_drills = [
            {"cat": "Conditioning", "ex": "JUMP ROPE", "desc": "Rhythmic coordination.", "base": 2, "unit": "min", "loc": "Gym", "focus": ["Wrist Spin", "Light Feet"]},
            {"cat": "Strength", "ex": "PUSHUPS", "desc": "Upper body pressing strength.", "base": 15, "unit": "reps", "loc": "Gym", "focus": ["Elbow Path", "Full ROM"]},
            {"cat": "Power", "ex": "BURPEES", "desc": "Full-body conditioning.", "base": 12, "unit": "reps", "loc": "Gym", "focus": ["Chest to Floor", "Speed"]},
            {"cat": "Strength", "ex": "GOBLET SQUATS", "desc": "Lower body strength.", "base": 12, "unit": "reps", "loc": "Weight Room", "focus": ["Depth", "Chest Up"]},
            {"cat": "Strength", "ex": "DUMBBELL ROW", "desc": "Unilateral pulling power.", "base": 10, "unit": "reps", "loc": "Weight Room", "focus": ["Scapular Pull", "Control"]},
            {"cat": "Mobility", "ex": "BEAR CRAWLS", "desc": "Total body mobility.", "base": 20, "unit": "meters", "loc": "Gym", "focus": ["Low Hips", "Stability"]},
            {"cat": "Strength", "ex": "LUNGES", "desc": "Unilateral leg strength.", "base": 10, "unit": "reps", "loc": "Gym", "focus": ["Knee Track", "Upright"]},
            {"cat": "Conditioning", "ex": "MOUNTAIN CLIMBERS", "desc": "Core-integrated cardio.", "base": 45, "unit": "sec", "loc": "Gym", "focus": ["Flat Back", "Rapid Drive"]}
        ]
        return [d for d in general_drills if d['loc'] in locs]
    
    return []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:12px; color:{accent};">TODAY'S DATE</p>
        <p style="margin:0; font-size:18px; font-weight:900;">{get_now_est().strftime('%B %d, %Y')}</p>
    </div>""", unsafe_allow_html=True)

    sport_choice = st.selectbox("Select Sport", ["Basketball", "Softball", "Track", "General"])
    
    with st.expander("📍 LOCATIONS", expanded=True):
        active_locs = []
        for loc in ["Gym", "Track", "Weight Room", "Batting Cages", "Softball Field"]:
            if st.checkbox(loc, value=True, key=f"loc_{loc}"):
                active_locs.append(loc)

    active_cats = None
    if sport_choice == "Basketball":
        with st.expander("🏀 CATEGORIES", expanded=True):
            all_cats = ["Warm-up", "Crossover", "Combos", "Between Legs", "On the Move", "Behind Back", "Fakes", "Post-Up", "Transition", "Slide Series", "Float Series", "Jabs", "Stop Series", "Retreats", "Twitchy", "Drop Series", "Spins", "Stationary", "Contact", "2-Ball", "Tennis Ball"]
            active_cats = [cat for cat in all_cats if st.checkbox(cat, value=True, key=f"cat_{cat}")]
    
    difficulty = st.select_slider("Intensity Level", options=["Standard", "Elite", "Pro"], value="Elite")
    
    st.markdown(f"""<div class="sidebar-card">
        <p style="margin:0; font-size:11px; color:{accent};">STREAK</p>
        <p style="margin:0; font-size:22px; font-weight:900;">{st.session_state.streak} DAYS</p>
    </div>""", unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.title(f"PRO-ATHLETE TRACKER: {sport_choice.upper()}")

drills = get_workout_template(sport_choice, active_locs, active_cats)
target_mult = {"Standard": 1.0, "Elite": 1.5, "Pro": 2.0}[difficulty]
rest_mult = {"Standard": 1.0, "Elite": 0.8, "Pro": 0.5}[difficulty]

if not drills:
    st.warning("Please check your filters in the sidebar.")
else:
    completed_drills = sum([st.session_state.get(f"done_{i}", False) for i in range(len(drills))])
    progress = completed_drills / len(drills)
    st.progress(progress)
    st.caption(f"Workout Completion: {completed_drills} / {len(drills)} Drills")

    for i, item in enumerate(drills):
        st.markdown(f'<div class="drill-header">[{item["cat"].upper()}] {item["ex"]}</div>', unsafe_allow_html=True)
        st.write(item["desc"])
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: 
            sets = st.text_input("Sets", value="3", key=f"sets_{i}")
        with c2: 
            val = int(item["base"] * target_mult)
            reps = st.text_input("Reps/Unit", value=f"{val} {item['unit']}", key=f"reps_{i}")
        with c3: 
            st.checkbox("Mark Done", key=f"done_{i}")
        
        f_cols = st.columns(len(item["focus"]))
        for idx, pt in enumerate(item["focus"]):
            with f_cols[idx]: st.caption(f"🎯 {pt}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"LOG ✅", key=f"log_{i}", use_container_width=True):
                entry = {
                    "Time": get_now_est().strftime("%H:%M"),
                    "Drill": item["ex"],
                    "Result": f"{sets} x {reps}"
                }
                st.session_state.history.append(entry)
                st.toast(f"{item['ex']} Logged")
        with col_b:
            rest_v = int(30 * rest_mult) 
            if st.button(f"REST {rest_v}s ⏱️", key=f"rest_{i}", use_container_width=True):
                ph = st.empty()
                for t in range(rest_v, -1, -1):
                    ph.markdown(f"<p style='text-align:center; font-size:32px; color:{electric_blue}; font-weight:900;'>{t}s</p>", unsafe_allow_html=True)
                    time.sleep(1)
                ph.empty()

# --- 6. HISTORY & ARCHIVE ---
st.divider()
if st.session_state.history:
    with st.expander("📋 LIVE SESSION HISTORY"):
        st.table(pd.DataFrame(st.session_state.history))

if st.button("💾 ARCHIVE COMPLETE SESSION", use_container_width=True):
    st.session_state.streak += 1
    st.balloons()
    st.success("Session Archived! Streak +1")
