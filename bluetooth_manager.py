import bluetooth
import time
import excel_manager

RSSI_THRESHOLD = -80

def is_bluetooth_available():
    try:
        bluetooth.discover_devices(duration=1, lookup_names=False)
        return True
    except Exception:
        return False

def get_rssi(mac):
    """
    Attempt to read RSSI for a device.
    Falls back to -55 if platform doesn't support it.
    """
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((mac, 1))
        # This is a bit of a hack as getsockopt might not always return RSSI on all platforms
        # But we use it as a best-effort.
        rssi = sock.getsockopt(bluetooth.SOL_BLUETOOTH, bluetooth.BT_SECURITY)
        sock.close()
        return rssi
    except Exception:
        pass
    
    # Fallback for devices that are discovered
    return -55

def scan_nearby_macs(duration=5):
    """Returns list of (mac, rssi) tuples."""
    results = []
    try:
        nearby = bluetooth.discover_devices(
            duration=duration,
            lookup_names=False,
            flush_cache=True,
            lookup_class=False
        )
        for mac in nearby:
            rssi = get_rssi(mac)
            results.append((mac.upper(), rssi))
    except Exception as e:
        print(f"Bluetooth scan error: {e}")
    return results

def scan_and_register(roll_no, student_name):
    """
    Scans for 8 seconds, finds new devices, picks closest one, registers it.
    """
    if not is_bluetooth_available():
        return {"success": False, "error": "Bluetooth hardware not available or disabled."}
    
    print(f"Scanning for registration: {student_name} ({roll_no})")
    try:
        # scan for 8 seconds
        nearby_devices = bluetooth.discover_devices(
            duration=8,
            lookup_names=True,
            flush_cache=True
        )
        
        if not nearby_devices:
            return {"success": False, "error": "No Bluetooth devices detected. Make sure your Bluetooth is ON and discoverable."}
        
        # Filter out already registered devices
        new_candidates = []
        for mac, name in nearby_devices:
            mac_upper = mac.upper()
            if not excel_manager.student_already_registered(mac_upper):
                rssi = get_rssi(mac)
                new_candidates.append({
                    "mac": mac_upper,
                    "name": name,
                    "rssi": rssi
                })
        
        if not new_candidates:
            return {"success": False, "error": "No new devices found. All nearby devices are already registered."}
        
        # Pick the one with the strongest RSSI (closest to 0)
        # Sort by RSSI descending
        new_candidates.sort(key=lambda x: x["rssi"], reverse=True)
        best_match = new_candidates[0]
        
        # Register in Excel
        success = excel_manager.save_mac_registration(roll_no, best_match["mac"], best_match["name"] or "Unknown Device")
        
        if success:
            masked_mac = f"{best_match['mac'][:6]}:XX:XX:XX:XX"
            return {
                "success": True, 
                "mac": masked_mac, 
                "full_mac": best_match["mac"],
                "device_name": best_match["name"],
                "device_count": len(nearby_devices)
            }
        else:
            return {"success": False, "error": "Roll number not found in student list."}
            
    except Exception as e:
        return {"success": False, "error": f"Scanning failed: {str(e)}"}
