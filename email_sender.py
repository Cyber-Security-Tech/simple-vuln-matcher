import smtplib
import os
from email.message import EmailMessage

# Configure your Gmail credentials here
EMAIL_ADDRESS = "cyberilyas123@gmail.com"
EMAIL_PASSWORD = "qlbz ppdy apqz isen"

def send_email(recipient_email):
    """Sends the vulnerability scan report to the user via email."""
    msg = EmailMessage()
    msg["Subject"] = "Your Vulnerability Scan Report"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg.set_content("Attached is your vulnerability scan report.")

    # Attach the PDF & CSV reports
    files = ["vulnerabilities_report.pdf", "vulnerabilities_filtered.csv"]
    
    for file in files:
        if os.path.exists(file):
            with open(file, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"📧 Email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"❌ Email failed to send: {e}")
