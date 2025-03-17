import time
import csv
import json
import schedule
from datetime import datetime
from software_scanner import get_installed_software
from nvd_api import fetch_nvd_vulnerabilities
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from jinja2 import Template

def shorten_description(description, max_length=100):
    """Shortens long descriptions and adds '...' at the end."""
    return description if len(description) <= max_length else description[:max_length] + "..."

def check_installed_vulnerabilities(software_list):
    """Checks each installed software for vulnerabilities using the NVD API."""
    results = []
    print("\n🔍 Scanning installed software for vulnerabilities...\n")

    for software in software_list:
        name = software["name"]
        version = software["version"]
        print(f"Checking {name} {version}...")

        vulnerabilities = fetch_nvd_vulnerabilities(name)

        print(f"Found {len(vulnerabilities)} High/Critical vulnerabilities for {name}\n")

        if vulnerabilities:
            for vuln in vulnerabilities:
                results.append([name, version, vuln["cve_id"], vuln["severity"], vuln["description"]])

        time.sleep(5)  # Wait 5 seconds to avoid API rate limits

    return results

def export_to_csv(vulnerabilities, filename="vulnerabilities_filtered.csv"):
    """Exports vulnerabilities to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Software", "Version", "CVE ID", "Severity", "Description"])
        writer.writerows(vulnerabilities)
    print(f"\n📂 Report saved as {filename}")

def export_to_json(vulnerabilities, filename="vulnerabilities_filtered.json"):
    """Exports vulnerabilities to a JSON file."""
    json_data = [
        {"Software": s, "Version": v, "CVE ID": cve, "Severity": sev, "Description": desc}
        for s, v, cve, sev, desc in vulnerabilities
    ]
    with open(filename, mode="w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)
    print(f"\n📂 Report saved as {filename}")

def export_to_pdf(vulnerabilities, filename="vulnerabilities_report.pdf"):
    """Exports vulnerabilities to a formatted PDF."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    def add_page_header():
        """Adds a header at the top of each new page."""
        c.drawString(200, 750, "Vulnerability Report (Continued)")
        c.drawString(200, 735, "-------------------------------------------")
        return 720

    c.drawString(200, 750, "Vulnerability Report (High & Critical Only)")
    c.drawString(200, 735, "-------------------------------------------")

    y_position = 720
    max_width = 500
    line_height = 15

    for software, version, cve_id, severity, description in vulnerabilities:
        if y_position < 150:  
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = add_page_header()

        c.drawString(50, y_position, f"Software: {software} ({version})")
        y_position -= line_height
        c.drawString(50, y_position, f"CVE ID: {cve_id} | Severity: {severity}")
        y_position -= line_height

        wrapped_description = simpleSplit(description, "Helvetica", 12, max_width)
        for line in wrapped_description:
            c.drawString(50, y_position, line)
            y_position -= line_height

        y_position -= 20
        c.drawString(50, y_position, "-" * 90)
        y_position -= 20

    c.save()
    print(f"\n📂 Report saved as {filename}")

def log_scan_history():
    """Logs the scan results to a history file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("scan_history.txt", "a", encoding="utf-8") as file:
        file.write(f"\n🔄 Scan completed at {timestamp}\n")
    print(f"\n📝 Scan history updated: {timestamp}")

def run_vulnerability_scan():
    """Runs an immediate vulnerability scan and generates reports."""
    installed_software = get_installed_software()
    vulnerability_results = check_installed_vulnerabilities(installed_software)

    export_to_csv(vulnerability_results)
    export_to_json(vulnerability_results)
    export_to_pdf(vulnerability_results)
    log_scan_history()

    print("\n✅ Scan completed!")

def run_scheduled_scan():
    """Runs a scheduled scan based on user-defined time."""
    print("\n⏳ Running scheduled vulnerability scan...\n")
    run_vulnerability_scan()

def set_schedule():
    """Asks the user to set a time for daily automatic scans."""
    while True:
        scan_time = input("\n⏰ Enter the time for daily scheduled scan (HH:MM, 24-hour format): ").strip()
        if len(scan_time) == 5 and scan_time[2] == ":":
            try:
                hour, minute = map(int, scan_time.split(":"))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    schedule.every().day.at(scan_time).do(run_scheduled_scan)
                    print(f"\n✅ Scheduled scans set for {scan_time} every day.")
                    return
            except ValueError:
                pass
        print("❌ Invalid time format. Please enter time as HH:MM (24-hour format).")

if __name__ == "__main__":
    print("\n📌 Welcome to Simple Vulnerability Matcher")
    print("\nChoose an option:")
    print("1️⃣ Run a scan immediately")
    print("2️⃣ Set up a scheduled daily scan")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        run_vulnerability_scan()
    elif choice == "2":
        set_schedule()
        print("\n🔄 Automatic scanning enabled. The program will now run in the background.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("\n❌ Invalid choice. Please restart and choose either 1 or 2.")
