import time
import sqlite3
from datetime import datetime
from vuln_scanner import run_vulnerability_scan
from email_sender import send_email

DB_FILE = "schedules.db"

def get_scheduled_scan():
    """Fetch the scheduled scan time and email from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT scan_time, email FROM schedules LIMIT 1")
    scheduled_info = c.fetchone()
    conn.close()
    return scheduled_info

def check_and_run_scan():
    """Check if it's time to run the scheduled scan, then execute it."""
    while True:
        now = datetime.now().strftime("%H:%M")
        scheduled_scan = get_scheduled_scan()
        
        if scheduled_scan:
            scheduled_time, email = scheduled_scan
            print(f"⏳ Scheduled Scan: {scheduled_time}, Current Time: {now}")

            if now == scheduled_time:
                print("🚀 Running scheduled vulnerability scan...")
                run_vulnerability_scan()
                print("✅ Scan completed!")

                # Send email with reports
                send_email(email)
                print(f"📧 Report sent to {email}!")

                # Wait a minute before checking again to prevent duplicate scans
                time.sleep(60)

        else:
            print("🔄 No scheduled scans found. Checking again in 30 seconds.")

        time.sleep(30)

if __name__ == "__main__":
    print("🚀 Scheduled scan worker started...")
    check_and_run_scan()
