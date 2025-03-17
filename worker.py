import sqlite3
import schedule
import time
from datetime import datetime
from vuln_scanner import run_vulnerability_scan

def get_scheduled_time():
    """Retrieves the scheduled scan time from the database."""
    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute("SELECT scan_time FROM schedules LIMIT 1")
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def run_scheduled_scan():
    """Runs a scheduled vulnerability scan."""
    print("\n⏳ Running scheduled vulnerability scan...\n")
    run_vulnerability_scan()
    print("\n✅ Scheduled scan completed!")

def check_and_schedule():
    """Checks if a scan is scheduled and sets it up."""
    scan_time = get_scheduled_time()
    if scan_time:
        schedule.clear()  # Remove old scheduled tasks
        schedule.every().day.at(scan_time).do(run_scheduled_scan)
        print(f"\n✅ Scheduled scan set for {scan_time} every day.")

# Run on startup
check_and_schedule()

# Background loop to keep checking for schedules
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
