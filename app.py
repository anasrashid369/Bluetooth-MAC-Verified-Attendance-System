from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import bluetooth_manager
import excel_manager
import threading
import time
import socket
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global state for attendance
attendance_state = {
    "running": False,
    "start_time": None,
    "present": {},  # roll_no -> {name, time, rssi}
    "absent": set(), # roll_no
    "remaining_seconds": 900,
    "total_students": 0
}

state_lock = threading.Lock()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def attendance_thread_func():
    global attendance_state
    
    students = excel_manager.load_students()
    registered_students = {s["mac"].upper(): s for s in students if s["mac"]}
    all_roll_nos = {s["roll_no"] for s in students}
    
    with state_lock:
        attendance_state["total_students"] = len(students)
        attendance_state["absent"] = all_roll_nos.copy()
        attendance_state["present"] = {}
        attendance_state["start_time"] = time.time()
    
    duration = 900 # 15 minutes
    
    while True:
        with state_lock:
            if not attendance_state["running"]:
                break
            
            elapsed = time.time() - attendance_state["start_time"]
            remaining = duration - elapsed
            attendance_state["remaining_seconds"] = max(0, int(remaining))
            
            if remaining <= 0:
                attendance_state["running"] = False
                break
        
        # Scan for devices
        nearby = bluetooth_manager.scan_nearby_macs(duration=5)
        
        with state_lock:
            for mac, rssi in nearby:
                if mac in registered_students:
                    student = registered_students[mac]
                    roll = student["roll_no"]
                    
                    if roll not in attendance_state["present"]:
                        if rssi >= bluetooth_manager.RSSI_THRESHOLD:
                            now_str = datetime.now().strftime("%H:%M:%S")
                            attendance_state["present"][roll] = {
                                "name": student["name"],
                                "time": now_str,
                                "rssi": rssi
                            }
                            if roll in attendance_state["absent"]:
                                attendance_state["absent"].remove(roll)
                            
                            # Update Excel immediately
                            excel_manager.mark_present(roll, mac, rssi, now_str)
        
        time.sleep(1) # Small gap between scans

    # Finalize: mark remaining as absent in Excel
    with state_lock:
        remaining_absent = list(attendance_state["absent"])
        for roll in remaining_absent:
            excel_manager.mark_absent(roll)
        attendance_state["running"] = False

# --- Routes ---

@app.route('/')
def teacher_dashboard():
    return render_template('teacher_dashboard.html', local_ip=get_local_ip())

@app.route('/register')
def student_register():
    return render_template('student_register.html')

@app.route('/attendance/live')
def attendance_live():
    return render_template('attendance_live.html')

@app.route('/api/students')
def get_students():
    return jsonify(excel_manager.load_students())

@app.route('/api/registration-status')
def registration_status():
    students = excel_manager.load_students()
    return jsonify(students)

@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.json
    roll_no = data.get('roll_no')
    name = data.get('name')
    
    if not roll_no or not name:
        return jsonify({"success": False, "error": "Roll number and name are required."})
    
    # Check if student exists
    students = excel_manager.load_students()
    student = next((s for s in students if s["roll_no"] == roll_no), None)
    
    if not student:
        return jsonify({"success": False, "error": "Roll number not found — check with your teacher."})
    
    if student["mac"]:
        return jsonify({"success": False, "error": "You are already registered."})
    
    # Trigger scan and registration
    result = bluetooth_manager.scan_and_register(roll_no, name)
    return jsonify(result)

@app.route('/api/attendance/start', methods=['POST'])
def start_attendance():
    global attendance_state
    with state_lock:
        if attendance_state["running"]:
            return jsonify({"success": False, "error": "Attendance is already running."})
        
        if not bluetooth_manager.is_bluetooth_available():
            return jsonify({"success": False, "error": "Bluetooth hardware not detected."})
            
        attendance_state["running"] = True
        thread = threading.Thread(target=attendance_thread_func)
        thread.daemon = True
        thread.start()
        
    return jsonify({"success": True})

@app.route('/api/attendance/stop', methods=['POST'])
def stop_attendance():
    global attendance_state
    with state_lock:
        attendance_state["running"] = False
    return jsonify({"success": True})

@app.route('/api/attendance/status')
def attendance_status():
    with state_lock:
        students = excel_manager.load_students()
        full_list = []
        for s in students:
            status = "PENDING"
            detected_time = "-"
            rssi = "-"
            
            if s["roll_no"] in attendance_state["present"]:
                status = "PRESENT"
                detected_time = attendance_state["present"][s["roll_no"]]["time"]
                rssi = attendance_state["present"][s["roll_no"]]["rssi"]
            elif not attendance_state["running"] and s["roll_no"] in attendance_state["absent"]:
                # If stopped, we can show ABSENT
                status = "ABSENT"
            
            full_list.append({
                "roll_no": s["roll_no"],
                "name": s["name"],
                "status": status,
                "time": detected_time,
                "rssi": rssi
            })
            
        return jsonify({
            "is_running": attendance_state["running"],
            "remaining_seconds": attendance_state["remaining_seconds"],
            "present_count": len(attendance_state["present"]),
            "absent_count": len(attendance_state["absent"]) if not attendance_state["running"] else 0,
            "total_count": attendance_state["total_students"],
            "students": full_list
        })

@app.route('/api/export')
def export_excel():
    return send_file(excel_manager.EXCEL_FILE, as_attachment=True)

@app.route('/api/health')
def health_check():
    return jsonify({
        "bluetooth": bluetooth_manager.is_bluetooth_available(),
        "ip": get_local_ip()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
