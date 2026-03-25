"""
generate_random_data.py
=======================
HW1-1 Part 3: Insert random sensor data into aiotdb.db (SQLite3).

This simulates the data that would normally arrive via WiFi from the ESP32.
Run this script to populate the database so you can view it in DB Browser for SQLite.

Usage:
    python generate_random_data.py            # inserts 20 random rows (default)
    python generate_random_data.py 50         # inserts 50 random rows
"""

import sqlite3
import random
import datetime
import sys
import os

# ─── Configuration ────────────────────────────────────────────────────────────
DB_PATH     = os.path.join(os.path.dirname(__file__), "aiotdb.db")
TABLE_NAME  = "sensor_data"
NUM_ROWS    = int(sys.argv[1]) if len(sys.argv) > 1 else 20

# ─── Connect / Create DB ──────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id   TEXT    NOT NULL DEFAULT 'ESP32_DHT11_HW1',
        temperature REAL    NOT NULL,
        humidity    REAL    NOT NULL,
        recorded_at TEXT    NOT NULL
    )
""")
conn.commit()
print(f"[DB] Table '{TABLE_NAME}' ready in: {DB_PATH}")

# ─── Insert Random Rows ───────────────────────────────────────────────────────
base_time = datetime.datetime.now() - datetime.timedelta(minutes=NUM_ROWS * 2)

rows_inserted = 0
for i in range(NUM_ROWS):
    temp      = round(random.uniform(20.0, 35.0), 1)   # °C  (realistic room range)
    humidity  = round(random.uniform(40.0, 90.0), 1)   # %RH
    timestamp = (base_time + datetime.timedelta(minutes=i * 2)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (device_id, temperature, humidity, recorded_at) VALUES (?, ?, ?, ?)",
        ("ESP32_DHT11_HW1", temp, humidity, timestamp)
    )
    rows_inserted += 1
    print(f"  [{i+1:>3}/{NUM_ROWS}] {timestamp}  Temp={temp}°C  Humidity={humidity}%")

conn.commit()
conn.close()

print(f"\n[OK] Done! Inserted {rows_inserted} rows into '{TABLE_NAME}'.")
print(f"     Open aiotdb.db with 'DB Browser for SQLite' to view the data.")
