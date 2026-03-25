"""
esp32_sim.py — ESP32 DHT11 Simulator
======================================
Simulates a WiFi-connected ESP32 sending DHT11 sensor data
every 5 seconds via HTTP POST to the Flask /sensor endpoint.

No WiFi delay, packet loss, or network simulation.
Run:  python esp32_sim.py
"""

import requests
import random
import time
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
SERVER_URL  = "http://localhost:5000/sensor"
DEVICE_ID   = "ESP32_SIM_001"
IP_ADDRESS  = "192.168.137.100"   # Simulated ESP32 IP
INTERVAL    = 5                   # seconds between each POST

def generate_payload():
    """Generate realistic fake DHT11 + ESP32 WiFi metadata."""
    return {
        "device_id":   DEVICE_ID,
        "temperature": round(random.uniform(20.0, 35.0), 1),   # °C
        "humidity":    round(random.uniform(40.0, 90.0), 1),   # %RH
        "wifi_rssi":   random.randint(-80, -30),               # dBm
        "ip_address":  IP_ADDRESS
    }

def main():
    print("=" * 45)
    print("  ESP32 DHT11 Simulator")
    print(f"  Target : {SERVER_URL}")
    print(f"  Device : {DEVICE_ID}")
    print(f"  Interval: every {INTERVAL}s")
    print("=" * 45)

    seq = 0
    while True:
        seq += 1
        payload = generate_payload()
        ts = datetime.now().strftime("%H:%M:%S")

        try:
            resp = requests.post(SERVER_URL, json=payload, timeout=5)
            print(f"[{ts}] #{seq:04d}  temp={payload['temperature']}C  "
                  f"hum={payload['humidity']}%  rssi={payload['wifi_rssi']}dBm  "
                  f"→ {resp.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[{ts}] #{seq:04d}  ERROR: Cannot connect to {SERVER_URL}")
            print("         Make sure app.py is running (python app.py)")
        except Exception as e:
            print(f"[{ts}] #{seq:04d}  ERROR: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
