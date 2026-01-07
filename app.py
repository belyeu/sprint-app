<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Basketball Workout Generator</title>
    <style>
        :root {
            --bg-color: #f4f4f9;
            --text-color: #333;
            --card-bg: #ffffff;
            --primary-color: #ff6b00; /* Basketball Orange */
            --accent-color: #000;
            --border-color: #ddd;
            --btn-text-on-primary: #fff;
        }

        body.dark-mode {
            --bg-color: #121212;
            --text-color: #e0e0e0;
            --card-bg: #1e1e1e;
            --border-color: #333;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: background-color 0.3s, color 0.3s;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        h1 { margin: 0; font-size: 1.5rem; }

        /* --- Controls & Inputs --- */
        .controls {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }

        .input-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }

        input[type="range"] {
            width: 100%;
        }

        /* --- Buttons --- */
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9rem;
            transition: opacity 0.2s;
        }

        button:hover { opacity: 0.9; }

        /* The specific buttons requested to be BLACK text in dark mode */
        .btn-black-text {
            background-color: var(--primary-color);
            color: #000000 !important; /* Force black text always */
        }

        .btn-toggle {
            background-color: transparent;
            border: 1px solid var(--text-color);
            color: var(--text-color);
        }

        .btn-stop {
            background-color: #dc3545;
            color: white;
        }
        
        .btn-reset {
            background-color: #6c757d;
            color: white;
        }

        /* --- Timer/Stopwatch Section --- */
        .tools-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }

        .tool-card {
            background: var(--card-bg);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .timer-display {
            font-size: 2rem;
            font-family: monospace;
            margin: 10px 0;
            font-weight: bold;
        }

        /* --- Workout Output --- */
        .section-title {
            margin-top: 30px;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 5px;
            margin-bottom: 15px;
        }

        .drill-list {
            list-style: none;
            padding: 0;
        }

        .drill-item {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .drill-info h4 {
            margin: 0 0 5px 0;
            font-size: 1.1rem;
        }

        .drill-meta {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        
        .tag {
            display: inline-block;
            background: #eee;
            color: #333;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-right: 5px;
        }

        /* --- Responsive --- */
        @media (max-width: 600px) {
            .tools-section { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>🏀 Pro Trainer</h1>
        <button class="btn-toggle" onclick="toggleTheme()">Toggle Dark Mode</button>
    </header>

    <div class="controls">
        <div class="input-group">
            <label for="drillCount">Target Drills (Workout): <span id="drillCountVal">20</span></label>
            <input type="range" id="drillCount" min="5" max="30" value="20" oninput="document.getElementById('drillCountVal').innerText = this.value">
        </div>
        
        <button class="btn-black-text" onclick="generateWorkout()">Generate Workout</button>
    </div>

    <div class="tools-section">
        <div class="tool-card">
            <h3>Timer</h3>
            <div class="timer-display" id="timerDisplay">00:00</div>
            <div class="btn-group" style="justify-content: center;">
                <button class="btn-black-text" onclick="startTimer()">Start Timer</button>
                <button class="btn-stop" onclick="stopTimer()">Stop</button>
                <button class="btn-reset" onclick="resetTimer()">Reset</button>
            </div>
            <div style="margin-top:10px;">
                <input type="number" id="timerInput" placeholder="Min" style="width: 50px; padding: 5px;">
            </div>
        </div>

        <div class="tool-card">
            <h3>Stopwatch</h3>
            <div class="timer-display" id="stopwatchDisplay">00:00.00</div>
            <div class="btn-group" style="justify-content: center;">
                <button class="btn-black-text" onclick="startStopwatch()">Start Stopwatch</button>
                <button class="btn-stop" onclick="stopStopwatch()">Stop</button>
                <button class="btn-reset" onclick="resetStopwatch()">Reset</button>
            </div>
        </div>
    </div>

    <div id="workoutArea">
        <div id="warmupSection" style="display:none;">
            <h2 class="section-title">🔥 Warmup</h2>
            <p style="font-size: 0.9rem; opacity: 0.8;">Complete these before starting the main block.</p>
            <ul class="drill-list" id="warmupList"></ul>
        </div>

        <div id="mainWorkoutSection" style="display:none;">
            <h2 class="section-title">📋 Main Workout <span id="focusBadge" style="font-size:0.8rem; background:var(--primary-color); color:black; padding:2px 8px; border-radius:4px; vertical-align:middle; margin-left:10px;"></span></h2>
            <ul class="drill-list" id="workoutList"></ul>
        </div>
    </div>
</div>

<script>
    // --- 1. MOCK DATA (Simulating basketball.csv) ---
    // Types: Shooting, Movement, Footwork, Ball-handle, Finish, Defense, Warmup, W_room, Mental, Conditioning
    const basketballData = [
        // Warmups (Need enough to pick 6-10)
        { name: "Jump Rope", type: "Warmup" },
        { name: "High Knees", type: "Warmup" },
        { name: "Dynamic Stretching", type: "Warmup" },
        { name: "Line Hops", type: "Warmup" },
        { name: "Defensive Slides (Slow)", type: "Warmup" },
        { name: "Arm Circles", type: "Warmup" },
        { name: "Hip Openers", type: "Warmup" },
        { name: "Ankle Flips", type: "Warmup" },
        { name: "Light Jog", type: "Warmup" },
        { name: "Glute Bridges", type: "Warmup" },
        { name: "Form Shooting (Close)", type: "Warmup" },
        
        // Shooting
        { name: "3pt Around the World", type: "Shooting" },
        { name: "Free Throws (10 in a row)", type: "Shooting" },
        { name: "Mid-Range Pull ups", type: "Shooting" },
        { name: "Catch and Shoot (Wing)", type: "Shooting" },
        { name: "Catch and Shoot (Corner)", type: "Shooting" },
        { name: "Elbow Jumpers", type: "Shooting" },
        { name: "Step Back 3s", type: "Shooting" },
        { name: "Transition 3s", type: "Shooting" },
        
        // Ball-handle
        { name: "2 Ball Dribbling", type: "Ball-handle" },
        { name: "Crossover Series", type: "Ball-handle" },
        { name: "Behind the Back Wrap", type: "Ball-handle" },
        { name: "Spider Dribble", type: "Ball-handle" },
        { name: "Tennis Ball Toss", type: "Ball-handle" },
        { name: "Cone Weave", type: "Ball-handle" },

        // Finish
        { name: "Mikan Drill", type: "Finish" },
        { name: "Reverse Layups", type: "Finish" },
        { name: "Euro Step Finish", type: "Finish" },
        { name: "Floater Series", type: "Finish" },
        { name: "Contact Layups", type: "Finish" },

        // Defense
        { name: "Lane Agility", type: "Defense" },
        { name: "Closeouts", type: "Defense" },
        { name: "Box Out Drills", type: "Defense" },
        { name: "Full Court Slides", type: "Defense" },

        // Footwork
        { name: "Pivot Series", type: "Footwork" },
        { name: "Drop Steps", type: "Footwork" },
        { name: "Jab Step Series", type: "Footwork" },

        // Movement
        { name: "V-Cuts", type: "Movement" },
        { name: "L-Cuts", type: "Movement" },
        { name: "Backdoor Cuts", type: "Movement" },

        // Other (Conditioning, Mental, etc - for fallback)
        { name: "Suicides", type: "Conditioning" },
        { name: "17s", type: "Conditioning" },
        { name: "Visualization", type: "Mental" },
        { name: "Film Study", type: "Mental" },
        
        // Excluded from Algorithm
        { name: "Bench Press", type: "W_room" },
        { name: "Squats", type: "W_room" }
    ];

    // --- 2. GENERATION LOGIC ---

    function generateWorkout() {
        const targetCount = parseInt(document.getElementById('drillCount').value);
        
        // A. Handle Warmups (6-10 random)
        const allWarmups = basketballData.filter(d => d.type.toLowerCase() === 'warmup');
        const warmupCount = Math.floor(Math.random() * (10 - 6 + 1)) + 6; // Random between 6 and 10
        const selectedWarmups = getRandomItems(allWarmups, warmupCount);
        renderList('warmupList', selectedWarmups);
        document.getElementById('warmupSection').style.display = 'block';

        // B. Handle Main Workout
        // 1. Define Core Types
        const coreTypes = ['Shooting', 'Movement', 'Footwork', 'Ball-handle', 'Finish', 'Defense'];
        
        // 2. Randomly Select ONE Focus Type
        const randomFocus = coreTypes[Math.floor(Math.random() * coreTypes.length)];
        
        // 3. Filter Data for that Focus
        const focusDrills = basketballData.filter(d => d.type === randomFocus);
        
        let finalWorkout = [];
        let focusText = "";

        // 4. Algorithm Check
        if (focusDrills.length >= targetCount) {
            // Case 1: We have enough exercises in the random Focus Type
            finalWorkout = getRandomItems(focusDrills, targetCount);
            focusText = "Focus: " + randomFocus;
        } else {
            // Case 2: Not enough exercises -> Fallback 90/10 Logic
            focusText = "Focus: Mixed (Fallback)";
            
            // Calculate Split
            const countCore = Math.round(targetCount * 0.90);
            const countOther = targetCount - countCore;

            // Pool A: All Core Types (Shooting, Movement, etc.)
            const poolA = basketballData.filter(d => coreTypes.includes(d.type));
            
            // Pool B: Others (excluding Warmup, W_room, and Core Types)
            const excludedTypes = ['Warmup', 'W_room', ...coreTypes];
            const poolB = basketballData.filter(d => !excludedTypes.includes(d.type));

            // Select
            const selectedCore = getRandomItems(poolA, countCore);
            const selectedOther = getRandomItems(poolB, countOther);

            finalWorkout = [...selectedCore, ...selectedOther];
        }

        renderList('workoutList', finalWorkout, true);
        document.getElementById('focusBadge').innerText = focusText;
        document.getElementById('mainWorkoutSection').style.display = 'block';
    }

    // Helper: Select n random items from array
    function getRandomItems(arr, n) {
        const shuffled = [...arr].sort(() => 0.5 - Math.random());
        // If n is larger than array length, return whole array (or duplicate if you wanted strict counts, but usually returning max available is safer)
        return shuffled.slice(0, n);
    }

    // Helper: Render to HTML
    function renderList(elementId, items, addLogButton = false) {
        const list = document.getElementById(elementId);
        list.innerHTML = '';
        
        items.forEach(item => {
            const li = document.createElement('li');
            li.className = 'drill-item';
            
            let html = `
                <div class="drill-info">
                    <h4>${item.name}</h4>
                    <div class="drill-meta">
                        <span class="tag">${item.type}</span>
                    </div>
                </div>
            `;
            
            if (addLogButton) {
                // Ensure Log Set button is also Black text in dark mode
                html += `<button class="btn-black-text" onclick="alert('Set Logged for ${item.name}')">Log Set</button>`;
            }
            
            li.innerHTML = html;
            list.appendChild(li);
        });
    }

    // --- 3. TOOLS LOGIC (Timer/Stopwatch) ---

    // Timer Variables
    let timerInterval;
    let timerSeconds = 0;

    function startTimer() {
        clearInterval(timerInterval);
        const input = document.getElementById('timerInput').value;
        if(timerSeconds === 0 && input) {
            timerSeconds = parseInt(input) * 60;
        }
        
        if (timerSeconds <= 0) return;

        timerInterval = setInterval(() => {
            timerSeconds--;
            updateTimerDisplay();
            if (timerSeconds <= 0) {
                clearInterval(timerInterval);
                alert("Time's up!");
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
    }

    function resetTimer() {
        stopTimer();
        timerSeconds = 0;
        updateTimerDisplay();
    }

    function updateTimerDisplay() {
        const m = Math.floor(timerSeconds / 60).toString().padStart(2, '0');
        const s = (timerSeconds % 60).toString().padStart(2, '0');
        document.getElementById('timerDisplay').innerText = `${m}:${s}`;
    }

    // Stopwatch Variables
    let stopwatchInterval;
    let stopwatchStartTime;
    let stopwatchElapsedTime = 0;

    function startStopwatch() {
        // Prevent multiple intervals
        clearInterval(stopwatchInterval); 
        stopwatchStartTime = Date.now() - stopwatchElapsedTime;
        
        stopwatchInterval = setInterval(() => {
            stopwatchElapsedTime = Date.now() - stopwatchStartTime;
            updateStopwatchDisplay();
        }, 10);
    }

    function stopStopwatch() {
        clearInterval(stopwatchInterval);
    }

    function resetStopwatch() {
        stopStopwatch();
        stopwatchElapsedTime = 0;
        updateStopwatchDisplay();
    }

    function updateStopwatchDisplay() {
        const time = new Date(stopwatchElapsedTime);
        const m = time.getUTCMinutes().toString().padStart(2, '0');
        const s = time.getUTCSeconds().toString().padStart(2, '0');
        const ms = Math.floor(time.getUTCMilliseconds() / 10).toString().padStart(2, '0');
        document.getElementById('stopwatchDisplay').innerText = `${m}:${s}.${ms}`;
    }

    // --- 4. THEME LOGIC ---
    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
    }
</script>

</body>
</html>
