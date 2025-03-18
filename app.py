import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_file, jsonify
from vuln_scanner import run_vulnerability_scan
from email_sender import send_email

app = Flask(__name__)

DB_FILE = "schedules.db"

# Ensure database exists
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY, scan_time TEXT, email TEXT)")
    conn.commit()
    conn.close()

def save_schedule(scan_time, email):
    """Saves the scheduled scan time and email securely."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM schedules")  # Only one schedule at a time
    c.execute("INSERT INTO schedules (scan_time, email) VALUES (?, ?)", (scan_time, email))
    conn.commit()
    conn.close()

def get_scheduled_scan():
    """Fetches the scheduled scan details from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT scan_time, email FROM schedules LIMIT 1")
    scheduled_info = c.fetchone()
    conn.close()
    return scheduled_info

def check_reports_exist():
    """Checks if all report files exist."""
    return (os.path.exists("vulnerabilities_filtered.csv") and
            os.path.exists("vulnerabilities_filtered.json") and
            os.path.exists("vulnerabilities_report.pdf"))

@app.route("/", methods=["POST", "GET"])
def index():
    """Handles the main page and user interactions."""
    message = ""

    if request.method == "POST":
        if "run_scan" in request.form:
            print("🚀 Running scan now...")
            run_vulnerability_scan()
            print("✅ Scan completed!")
            message = "✅ Scan completed! Reports are ready for download."

        elif "schedule_scan" in request.form:
            scan_time = request.form.get("scan_time")
            email = request.form.get("email")
            if scan_time and email:
                save_schedule(scan_time, email)
                print(f"✅ Scan scheduled daily at {scan_time}. The report will be sent to {email}.")
                message = f"✅ Scan scheduled daily at {scan_time}. The report will be sent to {email}."

    return render_template("index.html", message=message)

@app.route("/run_scan", methods=["POST"])
def run_scan():
    """Runs the scan immediately when the button is clicked."""
    print("🚀 Running scan now...")
    run_vulnerability_scan()
    print("✅ Scan completed!")
    return jsonify({"message": "Scan completed!"})

@app.route("/check_reports")
def check_reports():
    """API route for checking if reports are ready."""
    return jsonify({"reports_ready": check_reports_exist()})

@app.route("/delete_schedule", methods=["POST"])
def delete_schedule():
    """Deletes the scheduled scan entry from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM schedules")
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/download/<filetype>")
def download_file(filetype):
    """Serves the requested report file."""
    file_mapping = {
        "csv": "vulnerabilities_filtered.csv",
        "json": "vulnerabilities_filtered.json",
        "pdf": "vulnerabilities_report.pdf"
    }

    if filetype in file_mapping:
        file_path = os.path.join(os.getcwd(), file_mapping[filetype])

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return f"❌ Error: {file_mapping[filetype]} not found.", 404
    else:
        return "❌ Error: Invalid file type requested.", 400

if __name__ == "__main__":
    app.run(debug=True)
