from flask import Flask, render_template, request, jsonify, send_file
import threading
import schedule
import time
import os
from vuln_scanner import run_vulnerability_scan, set_schedule

app = Flask(__name__)

# Background thread to run scheduled tasks
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check for scheduled tasks every minute

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

@app.route("/")
def home():
    """Displays the home page."""
    return render_template("index.html")

@app.route("/run_scan", methods=["POST"])
def run_scan():
    """Runs an immediate vulnerability scan when the button is clicked."""
    run_vulnerability_scan()

    # Get filenames for download
    reports = {
        "pdf": "vulnerabilities_report.pdf",
        "csv": "vulnerabilities_filtered.csv",
        "json": "vulnerabilities_filtered.json",
        "html": "vulnerabilities_report.html",
    }

    return jsonify({
        "message": "Scan completed! Download the reports below.",
        "reports": reports
    })

@app.route("/schedule_scan", methods=["POST"])
def schedule_scan():
    """Allows the user to schedule a daily scan from the web UI."""
    scan_time = request.form.get("scan_time")  
    set_schedule(scan_time)  
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
