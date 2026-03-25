"""
app.py — HW1 AIoT Flask Server
================================
Receives DHT11 data from ESP32 (real or simulated) via HTTP POST.
Stores into SQLite3 aiotdb.db → sensors table.

Endpoints:
  POST /sensor       <- ESP32 / esp32_sim.py posts here
  GET  /health       <- health check
  GET  /sensor/data  <- last N rows (for Streamlit)
"""

from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")

# ─── DB Init ──────────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   TEXT    NOT NULL,
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            wifi_rssi   INTEGER,
            ip_address  TEXT,
            recorded_at TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] sensors table ready → {DB_PATH}")

# ─── POST /sensor ─────────────────────────────────────────────────────────────
@app.route("/sensor", methods=["POST"])
def receive_sensor():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    temp      = data.get("temperature")
    hum       = data.get("humidity")
    device_id = data.get("device_id", "ESP32_UNKNOWN")
    rssi      = data.get("wifi_rssi", None)
    ip        = data.get("ip_address", request.remote_addr)
    now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if temp is None or hum is None:
        return jsonify({"error": "Missing temperature or humidity"}), 400

    conn = get_conn()
    conn.execute(
        "INSERT INTO sensors (device_id, temperature, humidity, wifi_rssi, ip_address, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (device_id, float(temp), float(hum), rssi, ip, now)
    )
    conn.commit()
    conn.close()

    print(f"[POST] {now}  {device_id}  temp={temp}C  hum={hum}%  rssi={rssi}")
    return jsonify({"status": "ok", "recorded_at": now}), 200

# ─── GET /health ──────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    conn.close()
    return jsonify({
        "status": "ok",
        "db": DB_PATH,
        "total_records": count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200

# ─── GET /sensor/data ─────────────────────────────────────────────────────────
@app.route("/sensor/data", methods=["GET"])
def sensor_data():
    limit = request.args.get("limit", 50, type=int)
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sensors ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in reversed(rows)])

# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("[Server] Running on http://0.0.0.0:5000")
    print("[Server] Health check: http://localhost:5000/health")
    print("[Server] POST endpoint: http://localhost:5000/sensor")
    app.run(debug=False, host="0.0.0.0", port=5000)
