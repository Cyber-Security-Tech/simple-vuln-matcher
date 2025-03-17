import sqlite3
import time
import datetime
import schedule
from vuln_scanner import run_vulnerability_scan
from email_sender import send_email  # Ensure you have email support

def get_scheduled_scan():
    """Fetches the scheduled scan time and email from the database."""
    conn = sqlite3.connect("schedules.db")
    c = conn.cursor()
    c.execute("SELECT scan_time, email FROM schedules LIMIT 1")
    scheduled_info = c.fetchone()
    conn.close()
    return scheduled_info  # Returns (scan_time, email) or None if no schedule exists

def run_scheduled_scan():
    """Runs the vulnerability scan and sends the report via email."""
    print("🚀 Running scheduled vulnerability scan...")
    
    try:
        run_vulnerability_scan()
        print("✅ Scan completed successfully!")

        # Get the stored email from the database
        scheduled_info = get_scheduled_scan()
        if scheduled_info:
            email = scheduled_info[1]
            print(f"📧 Sending report to {email}...")
            send_email(email)
            print(f"📧 Report successfully sent to {email}!")

    except Exception as e:
        print(f"❌ Error running scan: {e}")

def check_and_schedule():
    """Checks if a scan is scheduled and runs it at the correct time."""
    scheduled_info = get_scheduled_scan()
    
    if scheduled_info:
        scan_time, email = scheduled_info
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        print(f"🕒 Current Time: {current_time}")
        print(f"📅 Scheduled Time: {scan_time}")
        
        if current_time == scan_time:
            print("🚀 Scheduled scan time reached! Running scan now...")
            run_scheduled_scan()
        else:
            print("⏳ Not time yet, waiting...")

# Schedule the check every minute
schedule.every(1).minutes.do(check_and_schedule)

# Run the scheduler loop
while True:
    print("🔄 Checking for scheduled scans...")
    schedule.run_pending()
    time.sleep(60)
