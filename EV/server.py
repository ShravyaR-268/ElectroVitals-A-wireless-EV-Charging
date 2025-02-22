from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import sqlite3

app = Flask(__name__)
CORS(app)

# Store relay status in memory (for real-time updates)
relay_status = {"relay1": "OFF", "relay2": "OFF"}

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        distance1 INTEGER,
                        distance2 INTEGER,
                        relay1 TEXT DEFAULT 'OFF',
                        relay2 TEXT DEFAULT 'OFF',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/get-data", methods=["GET"])
def get_data():
    distance1 = random.randint(5, 50)
    distance2 = random.randint(5, 50)

    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO readings (distance1, distance2, relay1, relay2) VALUES (?, ?, ?, ?)",
                   (distance1, distance2, relay_status["relay1"], relay_status["relay2"]))
    conn.commit()
    conn.close()

    return jsonify({"distance1": distance1, "distance2": distance2, "relay1": relay_status["relay1"], "relay2": relay_status["relay2"]})

@app.route("/control-relay", methods=["POST"])
def control_relay():
    relay_id = request.json.get("relay_id")
    status = request.json.get("status")

    if relay_id in relay_status:
        relay_status[relay_id] = status

        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE readings SET {relay_id} = ? ORDER BY timestamp DESC LIMIT 1", (status,))
        conn.commit()
        conn.close()

        return jsonify({"message": f"{relay_id} set to {status}"})
    else:
        return jsonify({"error": "Invalid relay ID"}), 400

@app.route("/get-history", methods=["GET"])
def get_history():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10")
    data = cursor.fetchall()
    conn.close()

    history = [{"id": row[0], "distance1": row[1], "distance2": row[2], "relay1": row[3], "relay2": row[4], "timestamp": row[5]} for row in data]
    return jsonify(history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
