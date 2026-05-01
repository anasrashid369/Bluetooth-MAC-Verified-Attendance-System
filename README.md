# 📡 Bluetooth MAC-Verified Attendance System

> A proxy-proof classroom attendance system that uses Bluetooth hardware MAC addresses and signal strength to verify physical presence — no extra hardware, no app installs, zero cost.
---

## 🚨 The Problem With Traditional Attendance

In most classrooms, a student can text a friend:
> *"bhai mark me present"*

And with name-based or manual systems — it works. One person can mark the entire class present from outside the room.

This system makes that **impossible.**

---

## ✅ How This Is Different

| Traditional Systems | This System |
|---|---|
| Trust device name (easily faked) | Ignores device name completely |
| No proximity check | RSSI signal must be ≥ -80 dBm (physically in room) |
| Manual or app-based | Fully automatic, no student app needed |
| Expensive hardware (RFID, fingerprint) | Uses laptop Bluetooth already in the classroom |
| Proxy possible | Proxy requires physically handing over your device |

---

## 🛡️ Security Architecture

The system verifies attendance through **two independent layers:**

### Layer 1 — MAC Address Verification
Every Bluetooth device has a **hardware MAC address** burned in at the factory (e.g. `A1:B2:C3:D4:E5:F6`). Unlike a device name which anyone can change in 5 seconds, a MAC address is tied to the physical hardware. During one-time registration, each student's MAC is permanently linked to their Roll Number in the Excel database.

### Layer 2 — RSSI Signal Strength (Physical Proximity)
RSSI (Received Signal Strength Indicator) measures how strong the Bluetooth signal is. The stronger the signal, the closer the device.

```
RSSI Value    Approx Distance    System Decision
-40 dBm   →  1–2 meters      →  ✅ PRESENT
-60 dBm   →  3–5 meters      →  ✅ PRESENT
-75 dBm   →  8–10 meters     →  ✅ PRESENT
-85 dBm   →  10–15 meters    →  ❌ TOO FAR — flagged
-90 dBm   →  Outside room    →  ❌ REJECTED
```

Both layers must pass. A valid MAC from outside the room = still rejected.

---

## ⚙️ How It Works

### Day 1 — One-Time Registration
```
Teacher runs the Flask server
         ↓
Teacher shares IP with class: "Open 192.168.1.x:5000/register on your phone"
         ↓
Student opens the page, enters Roll No + Name, clicks Register
         ↓
Server scans Bluetooth at that exact moment
         ↓
Detects student's device MAC → saves it to Excel permanently
         ↓
Student sees: "✅ Successfully Registered"
```

### Every Class — Attendance
```
Teacher opens localhost:5000 → clicks "Start Attendance"
         ↓
Background thread scans Bluetooth every 5 seconds for 15 minutes
         ↓
For each detected device:
    Is MAC registered? ──→ NO  ──→ Ignore (unknown device)
         ↓ YES
    Is RSSI ≥ -80 dBm? ──→ NO  ──→ Too far / possible proxy — skip
         ↓ YES
    Mark PRESENT ✅ — save to Excel with timestamp + signal strength
         ↓
After 15 minutes:
    All remaining undetected students → Mark ABSENT ❌
    Excel file saved automatically
```

---

## 🖥️ Features

**Teacher Dashboard** (`localhost:5000`)
- Live student grid with real-time PRESENT / ABSENT / PENDING status
- Countdown timer for the 15-minute attendance window
- One-click start and stop attendance
- Export attendance as Excel with one click
- Displays local IP so teacher can share the student registration link
- Bluetooth health indicator

**Student Registration Page** (`192.168.x.x:5000/register`)
- Mobile-first design, works on any phone browser
- No app install required
- Enter Roll No + Name → server detects your device automatically
- Clear error messages if device not found or already registered

**Live Attendance Monitor** (`localhost:5000/attendance/live`)
- Full-screen projectable view for the classroom
- Animated cards flip green as students are detected
- Live countdown timer and present/absent counters

---

## 🗂️ Project Structure

```
attendance_system/
├── app.py                      # Flask application & all API routes
├── bluetooth_manager.py        # Bluetooth scanning & RSSI logic (PyBluez)
├── excel_manager.py            # Excel read/write with thread-safe locking
├── attendance_register.xlsx    # Student database + attendance log
├── templates/
│   ├── base.html               # Shared navbar, fonts, TailwindCSS
│   ├── teacher_dashboard.html  # Teacher control panel
│   ├── student_register.html   # Student self-registration page
│   └── attendance_live.html    # Projectable live monitor
├── static/
│   └── app.js                  # Shared JS — polling, toasts, countdown
└── README.md
```

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/bluetooth-attendance-system.git
cd bluetooth-attendance-system
```

### 2. Install dependencies
```bash
pip install flask flask-cors openpyxl PyBluez2
```

> **Windows:** Run your terminal as **Administrator** — required for Bluetooth hardware access.
>
> **Linux:** You may need `sudo` and `bluetooth` + `libbluetooth-dev` packages:
> ```bash
> sudo apt install bluetooth libbluetooth-dev
> ```

### 3. Run the server
```bash
python app.py
```

### 4. Find your local IP address

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under your WiFi adapter e.g. 192.168.1.5
```

**Mac / Linux:**
```bash
ifconfig
# Look for "inet" under en0 or wlan0
```

### 5. Access the system

| Who | URL |
|---|---|
| Teacher | `http://localhost:5000` |
| Students (same WiFi) | `http://192.168.x.x:5000/register` |

> ⚠️ Teacher and students must be connected to the **same WiFi network.**

---

## 📋 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Teacher dashboard |
| GET | `/register` | Student registration page |
| POST | `/api/register` | Register a student's device |
| GET | `/api/registration-status` | All students + registered status |
| POST | `/api/attendance/start` | Start 15-minute attendance window |
| POST | `/api/attendance/stop` | Stop attendance early |
| GET | `/api/attendance/status` | Live status (present, absent, time left) |
| GET | `/api/students` | All students as JSON |
| GET | `/api/export` | Download Excel file |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+, Flask, Flask-CORS |
| Bluetooth | PyBluez2 (Classic Bluetooth, RFCOMM) |
| Excel | OpenPyXL |
| Concurrency | Python `threading` with `Lock()` |
| Frontend | HTML5, TailwindCSS (CDN), Vanilla JS |
| Database | Excel file (no database server needed) |

---

## ❓ FAQ

**Q: Can a student fake their MAC address?**
MAC spoofing requires root/admin access on the device, technical knowledge, and still won't help if they're not physically in range. Far more secure than any name-based or QR code system.

**Q: What if a student's phone is in their bag?**
Bluetooth signals pass through fabric easily. As long as the phone is in the room with Bluetooth ON, it will be detected.

**Q: Does the student need to do anything during class?**
No. After one-time registration, they just keep Bluetooth ON. The system detects them passively.

**Q: What if two students are on the same device?**
The one-time registration ties one MAC to one Roll Number. A device can only belong to one student.

**Q: Does this work with iPhones?**
Yes. iPhones are discoverable via Classic Bluetooth when the Bluetooth settings page is open or when the device was recently paired. Students may need to keep the Bluetooth settings screen open during the scan window.

---

## 🤝 Contributing

Pull requests are welcome. For major changes please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

## 👨‍💻 Author

Built with ❤️ as a solution to a real classroom problem.

If this helped you, consider giving it a ⭐ — it genuinely motivates further development.

> *"No extra hardware. No RFID cards. No fingerprint scanners. Just a laptop that every classroom already has."*
