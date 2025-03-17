import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
import threading
import schedule
import time
import os
from vuln_scanner import run_vulnerability_scan

app = Flask(__name__)

# Connect to SQLite database (creates if not exists)
def init_db():
    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY, scan_time TEXT)''')
    conn.commit()
    conn.close()

init_db()  # Initialize database on startup

@app.route("/")
def home():
    """Displays the home page."""
    return render_template("index.html")

@app.route("/run_scan", methods=["POST"])
def run_scan():
    """Runs an immediate vulnerability scan when the button is clicked."""
    run_vulnerability_scan()
    return jsonify({"message": "Scan completed! Download the reports below."})

@app.route("/schedule_scan", methods=["POST"])
def schedule_scan():
    """Stores the user-scheduled scan time in the database."""
    scan_time = request.form.get("scan_time")
    
    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute("DELETE FROM schedules")  # Remove old schedules (only allow one scan time)
    c.execute("INSERT INTO schedules (scan_time) VALUES (?)", (scan_time,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Scan scheduled daily at {scan_time}."})

@app.route("/download/<file_type>")
def download_file(file_type):
    """Handles downloading of the generated reports."""
    file_map = {
        "pdf": "vulnerabilities_report.pdf",
        "csv": "vulnerabilities_filtered.csv",
        "json": "vulnerabilities_filtered.json",
        "html": "vulnerabilities_report.html",
    }
    if file_type in file_map and os.path.exists(file_map[file_type]):
        return send_file(file_map[file_type], as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
