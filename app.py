import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
import os
from vuln_scanner import run_vulnerability_scan

app = Flask(__name__)

# Initialize database
def init_db():
    """Creates or updates the schedules database to store scan time and email."""
    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY, 
        scan_time TEXT, 
        email TEXT
    )''')
    conn.commit()
    conn.close()

init_db()  # Ensure database is set up

@app.route("/")
def home():
    """Displays the home page."""
    return render_template("index.html")

@app.route("/run_scan", methods=["POST"])
def run_scan():
    """Runs an immediate vulnerability scan."""
    run_vulnerability_scan()
    return jsonify({"message": "Scan completed! Download the reports below."})

@app.route("/schedule_scan", methods=["POST"])
def schedule_scan():
    """Stores the user's scheduled scan time and email in the database."""
    scan_time = request.form.get("scan_time")
    email = request.form.get("email")

    if not scan_time or not email:
        return jsonify({"error": "Scan time and email are required."}), 400

    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute("DELETE FROM schedules")  # Allow only one schedule at a time
    c.execute("INSERT INTO schedules (scan_time, email) VALUES (?, ?)", (scan_time, email))
    conn.commit()
    conn.close()

    return jsonify({"message": f"✅ Scan scheduled daily at {scan_time}. The report will be sent to {email} after the scan."})

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
