# Bluetooth Classroom Attendance System

A complete Flask-based local web application for automated attendance using Bluetooth scanning.

## Features
- **Teacher Dashboard**: Monitor attendance live, start/stop sessions, and export records.
- **Student Registration**: Easy mobile-first registration by scanning student devices.
- **Live Monitor**: High-visibility view for classroom projection.
- **Excel Integration**: All data is persisted in `attendance_register.xlsx`.
- **RSSI Verification**: Ensures students are physically present in the room.

## Prerequisites
- Python 3.8+
- Bluetooth adapter on the host machine.
- Windows: `pip install flask flask-cors openpyxl PyBluez2`
- Linux/Mac: `pip install flask flask-cors openpyxl pybluez`

## Setup & Running

1. **Install dependencies**:
   ```bash
   pip install flask flask-cors openpyxl PyBluez2
   ```

2. **Find your Local IP Address**:
   - **Windows**: Run `ipconfig` in CMD. Look for `IPv4 Address` under your WiFi adapter (e.g., `192.168.1.15`).
   - **Mac/Linux**: Run `ifconfig` or `ip addr`.

3. **Run the Application**:
   *Note: Run as Administrator on Windows for Bluetooth access.*
   ```bash
   python app.py
   ```

4. **Access the App**:
   - **Teacher Dashboard**: Open `http://localhost:5000` on your laptop.
   - **Student Registration**: Share `http://YOUR_IP:5000/register` with students.
   - **Live Monitor**: Open `http://localhost:5000/attendance/live` on the projector.

## Important Notes
- **WiFi**: Teacher and students must be on the same WiFi network.
- **Bluetooth**: Students must turn on Bluetooth and make their device "discoverable" during registration.
- **Proximity**: For registration, students should be within 2 meters of the laptop.

## Project Structure
- `app.py`: Flask server and background scanning thread.
- `bluetooth_manager.py`: Logic for Bluetooth discovery and RSSI reading.
- `excel_manager.py`: Thread-safe Excel read/write operations.
- `templates/`: HTML interfaces for teacher and student.
- `static/`: Frontend logic and styling.
