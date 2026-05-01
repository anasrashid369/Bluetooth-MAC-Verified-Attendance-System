let isRunning = false;
let remainingSeconds = 0;
let timerInterval = null;

async function startAttendance() {
    try {
        const r = await fetch('/api/attendance/start', { method: 'POST' });
        const data = await r.json();
        if (data.success) {
            showToast("Attendance window opened for 15 minutes", "success");
            pollAttendanceStatus();
        } else {
            showToast(data.error, "error");
        }
    } catch (e) {
        showToast("Failed to start attendance", "error");
    }
}

async function stopAttendance() {
    if (!confirm("Are you sure you want to stop attendance early?")) return;
    try {
        const r = await fetch('/api/attendance/stop', { method: 'POST' });
        const data = await r.json();
        if (data.success) {
            showToast("Attendance stopped manually", "info");
            pollAttendanceStatus();
        }
    } catch (e) {
        showToast("Failed to stop attendance", "error");
    }
}

async function pollAttendanceStatus() {
    try {
        const r = await fetch('/api/attendance/status');
        const data = await r.json();

        // Update counts
        if (document.getElementById('total-students')) {
            document.getElementById('total-students').innerText = data.total_count;
            document.getElementById('present-count').innerText = data.present_count;
            document.getElementById('absent-count').innerText = data.absent_count;
        }

        // Update UI state based on running status
        isRunning = data.is_running;
        remainingSeconds = data.remaining_seconds;

        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const timerDisplay = document.getElementById('timer-display');
        const progressContainer = document.getElementById('progress-container');

        if (startBtn && stopBtn) {
            if (isRunning) {
                startBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                timerDisplay.classList.remove('hidden');
                progressContainer.classList.remove('hidden');
                
                // Update progress bar
                const percent = data.total_count > 0 ? (data.present_count / data.total_count) * 100 : 0;
                document.getElementById('progress-bar').style.width = `${percent}%`;
                document.getElementById('progress-percent').innerText = `${Math.round(percent)}%`;
                
                startTimer();
            } else {
                startBtn.classList.remove('hidden');
                stopBtn.classList.add('hidden');
                timerDisplay.classList.add('hidden');
                progressContainer.classList.add('hidden');
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }

        // Update Student Grid if on dashboard
        const grid = document.getElementById('student-grid');
        if (grid) {
            updateStudentGrid(data.students);
        }

    } catch (e) {
        console.error("Poll error:", e);
    }
}

function updateStudentGrid(students) {
    const grid = document.getElementById('student-grid');
    
    // Sort: Present first, then Pending, then Absent
    const sorted = [...students].sort((a, b) => {
        const order = { 'PRESENT': 0, 'PENDING': 1, 'ABSENT': 2 };
        return order[a.status] - order[b.status];
    });

    // To prevent total re-render flicker, we can update in place or just clear if it's small
    // For this simple app, clearing is fine for now
    grid.innerHTML = '';
    
    sorted.forEach(s => {
        const card = document.createElement('div');
        const statusClasses = {
            'PRESENT': 'border-green-200 bg-white shadow-sm',
            'ABSENT': 'border-red-100 bg-red-50 opacity-80',
            'PENDING': 'border-gray-200 bg-white opacity-60'
        };
        
        const badgeClasses = {
            'PRESENT': 'bg-green-100 text-green-700',
            'ABSENT': 'bg-red-100 text-red-700',
            'PENDING': 'bg-gray-100 text-gray-700'
        };

        card.className = `p-5 rounded-2xl border ${statusClasses[s.status]} transition-all duration-500`;
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <span class="text-xs font-bold px-2 py-1 rounded-full ${badgeClasses[s.status]}">${s.status}</span>
                <span class="text-xs font-mono text-gray-400">${s.roll_no}</span>
            </div>
            <h3 class="font-bold text-gray-800 truncate">${s.name}</h3>
            ${s.status === 'PRESENT' ? `
                <div class="mt-4 flex justify-between items-center text-xs text-gray-500 font-medium">
                    <span>At ${s.time}</span>
                    <span class="flex items-center">
                        <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"></path></svg>
                        ${s.rssi} dBm
                    </span>
                </div>
            ` : ''}
        `;
        grid.appendChild(card);
    });
}

function startTimer() {
    if (timerInterval) return;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        if (remainingSeconds > 0) {
            remainingSeconds--;
            updateTimerDisplay();
        } else {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }, 1000);
}

function updateTimerDisplay() {
    const el = document.getElementById('timer-display');
    if (el) el.innerText = formatTime(remainingSeconds);
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const content = document.getElementById('toast-content');
    const msg = document.getElementById('toast-msg');
    
    const colors = {
        'success': 'bg-green-600',
        'error': 'bg-red-600',
        'info': 'bg-blue-600'
    };
    
    content.className = `px-6 py-3 rounded-lg shadow-2xl text-white font-medium flex items-center space-x-3 ${colors[type]}`;
    msg.innerText = message;
    
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
    
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 3000);
}
