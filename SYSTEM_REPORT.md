# HW1-1 System Report
## AIoT Sensor Monitoring System — ESP32 + DHT11 + Flask + SQLite + Streamlit

**Course:** 物聯網 (Internet of Things)  
**Student:** Kaiting Wu  
**Date:** 2026-03-25  
**Submission:** HW1-1 Client Side

---

## 1. System Overview

This project implements a full AIoT (Artificial Intelligence of Things) sensor monitoring pipeline using an ESP32 microcontroller paired with a DHT11 temperature and humidity sensor. Data is transmitted wirelessly over WiFi via HTTP POST to a local Flask server, persisted in a SQLite3 database, and visualized in real-time through a Streamlit dashboard.

A Python-based ESP32 simulator (`esp32_sim.py`) is also provided to replicate the ESP32's behavior locally for testing and demonstration without physical hardware.

### System Architecture

```
┌─────────────────────┐          HTTP POST          ┌──────────────────────┐
│  ESP32 + DHT11      │  ──────────────────────────► │  Flask Server        │
│  (Real Hardware)    │   /sensor  (every 3s)        │  app.py :5000        │
└─────────────────────┘                              └──────────┬───────────┘
                                                                │
┌─────────────────────┐          HTTP POST                      │ INSERT
│  esp32_sim.py       │  ──────────────────────────►            ▼
│  (Python Simulator) │   /sensor  (every 5s)        ┌──────────────────────┐
└─────────────────────┘                              │  SQLite3             │
                                                     │  aiotdb.db           │
                                                     │  sensors table       │
                                                     └──────────┬───────────┘
                                                                │
                                                                │ SELECT
                                                                ▼
                                                     ┌──────────────────────┐
                                                     │  Streamlit Dashboard │
                                                     │  dashboard.py :8501  │
                                                     │  Auto-refresh / 5s   │
                                                     └──────────────────────┘
```

---

## 2. Hardware Setup

### Components

| Component | Specification |
|-----------|---------------|
| Microcontroller | ESP32 Dev Module |
| Sensor | DHT11 (Temperature & Humidity) |
| Library | SimpleDHT (latest version) |

### Wiring

| DHT11 Pin | ESP32 GPIO |
|-----------|-----------|
| VCC | 3.3V |
| GND | GND |
| DATA | GPIO 15 (with 10kΩ pull-up recommended) |

| LED | ESP32 GPIO |
|-----|-----------|
| Built-in LED | GPIO 2 |

---

## 3. File Structure

```
HW1/
├── HW1_client/
│   └── HW1_client.ino       ESP32 main sketch
│                             - LED blink (GPIO 2, 500ms)
│                             - DHT11 read (GPIO 15, every 3s)
│                             - WiFi HTTP POST to /sensor
├── sketch_mar24b/
│   └── sketch_mar24b.ino    Reference sketch (DHT11 Serial only)
├── venv/                    Python virtual environment
├── app.py                   Flask server (receives & stores data)
├── esp32_sim.py             ESP32 Python simulator
├── dashboard.py             Streamlit real-time dashboard
├── generate_random_data.py  One-time random data seeder
├── requirements.txt         Python dependencies
├── aiotdb.db                SQLite3 database
├── DEVLOG.md                Development log
└── SYSTEM_REPORT.md         This file
```

---

## 4. Software Components

### 4.1 ESP32 Firmware — `HW1_client.ino`

Written in Arduino C++ for the ESP32 platform.

**Key behaviors:**
- **LED Flash:** GPIO 2 toggles every 500ms using `millis()` (non-blocking)
- **DHT11 Read:** Reads temperature and humidity every 3 seconds using `SimpleDHT11`
- **Serial Output:** Prints at 9600 baud in `sketch_mar24b` compatible format:
  ```
  =================================
  Humidity = 65% , Temperature = 28C
  ```
- **WiFi Upload:** Connects to WiFi on boot; sends JSON payload via HTTP POST every read cycle

**JSON Payload sent by ESP32:**
```json
{
  "device_id": "ESP32_DHT11_HW1",
  "temperature": 28,
  "humidity": 65
}
```

**Configuration:**

| Parameter | Value |
|-----------|-------|
| WiFi SSID | alvin |
| Server URL | `http://192.168.137.254:5000/sensor` |
| LED Pin | GPIO 2 |
| DHT11 Pin | GPIO 15 |
| Baud Rate | 9600 |
| Read Interval | 3000 ms |
| LED Interval | 500 ms |

---

### 4.2 Flask Server — `app.py`

Python Flask application listening on all interfaces at port 5000.

**Endpoints:**

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/sensor` | Receive DHT11 JSON data, insert into DB |
| `GET` | `/health` | Health check; returns status + record count |
| `GET` | `/sensor/data` | Return last N records as JSON |

**Database schema (`sensors` table):**

```sql
CREATE TABLE IF NOT EXISTS sensors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id   TEXT    NOT NULL,
    temperature REAL    NOT NULL,
    humidity    REAL    NOT NULL,
    wifi_rssi   INTEGER,
    ip_address  TEXT,
    recorded_at TEXT    NOT NULL
);
```

**Sample `/health` response:**
```json
{
  "status": "ok",
  "db": "C:\\...\\HW1\\aiotdb.db",
  "total_records": 12,
  "timestamp": "2026-03-25 17:24:55"
}
```

---

### 4.3 ESP32 Simulator — `esp32_sim.py`

Simulates a WiFi-connected ESP32 sending fake DHT11 data every 5 seconds.

**Simulated payload:**
```json
{
  "device_id": "ESP32_SIM_001",
  "temperature": 27.4,
  "humidity": 63.8,
  "wifi_rssi": -55,
  "ip_address": "192.168.137.100"
}
```

**Data ranges:**
- Temperature: 20.0 – 35.0 °C (uniform random)
- Humidity: 40.0 – 90.0 %RH (uniform random)
- WiFi RSSI: -80 – -30 dBm (random integer)

No WiFi delay, packet loss, or network simulation applied.

---

### 4.4 Streamlit Dashboard — `dashboard.py`

Real-time visualization dashboard that auto-refreshes every 5 seconds.

**Features:**
- **KPI Cards (4 columns):**
  - Total records in DB
  - Average temperature (with latest reading delta)
  - Average humidity (with latest reading delta)
  - Last updated timestamp
- **Temperature Line Chart** (°C over time)
- **Humidity Line Chart** (%RH over time)
- **Data Table** (last 20 records with all columns)

**Access URL:** `http://localhost:8501`

---

### 4.5 Dependencies — `requirements.txt`

```
flask
requests
streamlit
pandas
```

**Installed via virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

---

## 5. Service URLs

| Service | Local URL | Network URL |
|---------|-----------|-------------|
| Flask API | `http://localhost:5000` | `http://192.168.137.254:5000` |
| Health Check | `http://localhost:5000/health` | — |
| POST Endpoint | `http://localhost:5000/sensor` | `http://192.168.137.254:5000/sensor` |
| Streamlit Dashboard | `http://localhost:8501` | `http://192.168.137.254:8501` |

---

## 6. Startup Commands

Open **3 separate PowerShell terminals** in the `HW1/` directory:

```powershell
# Terminal 1 — Flask Server
.\venv\Scripts\python.exe app.py

# Terminal 2 — ESP32 Simulator
.\venv\Scripts\python.exe esp32_sim.py

# Terminal 3 — Streamlit Dashboard
.\venv\Scripts\streamlit.exe run dashboard.py
```

To also use the real ESP32:
1. Open `HW1_client/HW1_client.ino` in Arduino IDE
2. Upload to ESP32 (ensure SimpleDHT is at latest version)
3. Open Serial Monitor at **9600 baud**

---

## 7. Demo Screenshots

### Flask `/health` Endpoint
![Flask Health Check](screenshots/flask_health.png)

### Streamlit Dashboard — KPI & Charts
![Streamlit Dashboard](screenshots/streamlit_dashboard.png)

### Streamlit Dashboard — Data Table
![Streamlit Data Table](screenshots/streamlit_table.png)

---

## 8. Development Log

### 2026-03-24 — Initial Build

#### Project Initialization
- Created project workspace: `Desktop/物聯網/HW1/`
- Created `HW1_client/HW1_client.ino` with:
  - Non-blocking LED blink via `millis()`
  - DHT11 read using `SimpleDHT` library
  - WiFi HTTP POST scaffolding (commented out)
- Created `generate_random_data.py` — inserts 30 random rows into `aiotdb.db` to simulate historical WiFi data
- Created initial `app.py` Flask server

#### Issue 1 — DHT11 Output Format Mismatch
**Problem:** Serial output format in `HW1_client.ino` differed from the reference `sketch_mar24b.ino`.  
**Root Cause:** Different constructor style and `read()` API usage.  
**Fix:**
- Changed `SimpleDHT11 dht11(DHT11_PIN)` → `SimpleDHT11 dht11` (no-arg constructor)
- Changed `dht11.read(&temp, &hum, NULL)` → `dht11.read(DHT11_PIN, &temp, &hum, NULL)`
- Aligned Serial output to exact `sketch_mar24b` format:
  ```
  Humidity = X% , Temperature = XC
  ```

---

### 2026-03-25 — WiFi Integration & Full Pipeline

#### WiFi Setup
- Enabled full WiFi code in `HW1_client.ino`
- Initial SSID: `Kaiting's iPhone` (personal hotspot)

#### Issue 2 — Serial Monitor Garbled Output
**Problem:** Serial Monitor displayed garbage characters (`⸮⸮⸮QU⸮y⸮⸮$⸮`).  
**Root Cause:** Baud rate mismatch — sketch set `115200`, Serial Monitor set to `9600`.  
**Fix:** Changed `Serial.begin(115200)` → `Serial.begin(9600)`.

#### Issue 3 — WiFi Connection Failed (iPhone Hotspot)
**Problem:** ESP32 printed `[WiFi] Connection FAILED`.  
**Root Cause:** iPhone hotspot SSID `Kaiting's iPhone` uses Unicode curly apostrophe (`'` U+2019), which C string literals cannot match.  
**Fix:** Switched to standard WiFi AP (`alvin`).

#### Issue 4 — Connection Refused
**Problem:** ESP32 Serial showed `[WiFi] POST failed: connection refused`.  
**Root Cause:**
  - Flask server was not running on the PC
  - PC's IP changed from `172.20.10.2` (iPhone hotspot subnet) to `192.168.137.254` (alvin WiFi subnet)

**Fix:**
  - Updated `SERVER_URL` in `.ino` to `http://192.168.137.254:5000/api/sensor`
  - Started `app.py` with `python app.py`

#### Issue 5 — 404 Not Found
**Problem:** ESP32 received `404 Not Found` from server despite server running.  
**Root Cause:** Three Flask processes were simultaneously listening on port 5000 (leftover processes from previous sessions). Requests were being routed to an old `DIC4/app.py` instance that had no `/api/sensor` route.  
**Diagnosis:** `netstat -ano | findstr :5000` revealed 3 PIDs (21488, 29280, 17692) all on port 5000.  
**Fix:**
  ```powershell
  Stop-Process -Id 21488, 29280, 17692 -Force
  python app.py   # restart only HW1/app.py
  ```
**Verification:** Server log showed:
  ```
  192.168.137.146 - - [25/Mar/2026 17:08:56] "POST /api/sensor HTTP/1.1" 200 -
  ```

#### Full Pipeline Implementation (Teacher Prompt Compliance)

Updated system to fully satisfy course requirements:

| Requirement | Implementation |
|-------------|---------------|
| `esp32_sim.py` POST every 5s | Created; sends fake DHT11 + WiFi metadata |
| Flask `POST /sensor` | Renamed from `/api/sensor` |
| Flask `GET /health` | Added; returns status + record count |
| `sensors` table (not `sensor_data`) | Schema updated |
| Streamlit dashboard | Created with KPI, 2 charts, table |
| `venv` | Created at `HW1/venv/` |
| `requirements.txt` | Created: flask, requests, streamlit, pandas |
| Dependencies installed | All installed successfully |

Updated `HW1_client.ino` endpoint: `/api/sensor` → `/sensor`

#### Final Verification

```
✅ /health response:
   {"status": "ok", "total_records": 12, "timestamp": "2026-03-25 17:24:55"}

✅ esp32_sim.py posting successfully:
   127.0.0.1 - "POST /sensor HTTP/1.1" 200

✅ Streamlit running:
   Local URL:   http://localhost:8501
   Network URL: http://192.168.137.254:8501
```

---

## 9. Issues & Resolutions Summary

| # | Date | Problem | Root Cause | Fix |
|---|------|---------|------------|-----|
| 1 | 03-24 | DHT11 output format wrong | Mismatch with `sketch_mar24b` API style | Match no-arg constructor, `read(pin,...)`, Serial format |
| 2 | 03-25 | Serial garbled `⸮⸮⸮` | Baud rate 115200 ≠ Serial Monitor 9600 | `Serial.begin(9600)` |
| 3 | 03-25 | WiFi connection failed | iPhone `'` (U+2019) ≠ C `'` (U+0027) | Switch to `alvin` WiFi |
| 4 | 03-25 | `connection refused` | Server not running; IP changed after WiFi switch | Start `app.py`; update IP to `192.168.137.254` |
| 5 | 03-25 | `404 Not Found` | 3 stale Flask processes on port 5000, wrong one handled request | Kill all PIDs, restart only `HW1/app.py` |
| 6 | 03-25 | ESP32 still hitting `/api/sensor` | Endpoint renamed in new `app.py` but `.ino` not updated | Update `SERVER_URL` in `.ino` to `/sensor` |

---

## 10. HW1-1 Checklist

| Task | Status |
|------|--------|
| 1. LED Flash (GPIO 2, 500ms) | ✅ Done |
| 2. DHT11 data on Serial port | ✅ Done |
| 3. `aiotdb.db` random data visible in SQLite3 viewer | ✅ Done |
| 4. Via WiFi — HTTP POST success | ✅ Done |
| + `esp32_sim.py` simulator | ✅ Done |
| + Streamlit real-time dashboard | ✅ Done |
| + `venv` + `requirements.txt` | ✅ Done |
| + `/health` endpoint | ✅ Done |
