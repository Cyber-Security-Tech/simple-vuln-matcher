# 🔍 Simple Vulnerability Matcher

**Simple Vulnerability Matcher** is a cybersecurity tool that scans installed software on a Windows machine, checks for known vulnerabilities using the **NVD (National Vulnerability Database) API**, and generates detailed reports in **CSV, JSON, and PDF formats**.

---

## 🚀 Features
✔ **Scans Installed Software** – Detects software vulnerabilities from the NVD database.  
✔ **Generates Reports** – Creates reports in **CSV, JSON, and PDF** formats.  
✔ **Schedule Scans** – Allows users to set up daily automated scans with email report delivery.  
✔ **SQL Injection Protection** – Secure input handling for database queries.  
✔ **User-Friendly UI** – Web-based interface for running scans and downloading reports.  

---

## 🛠️ Installation & Setup
### **1. Clone the Repository**
```sh
git clone https://github.com/Cyber-Security-Tech/simple-vuln-matcher.git
cd simple-vuln-matcher
### **2. Install Dependencies**
pip install -r requirements.txt
### **3. Add Your API Key**
API_KEY = "your-api-key-here"
### **4. Run the Application**
python app.py
Then, open http://127.0.0.1:5000/ in your browser.

📂 Reports & Output
Once a scan completes, reports will be available for download:

CSV Report 📄 – /download/csv
JSON Report 📜 – /download/json
PDF Report 📑 – /download/pdf
If you schedule a scan, reports will be emailed to you.

💡 Why This Project? 
This project was built to demonstrate hands-on cybersecurity skills, including:
✅ API integration with the NVD vulnerability database
✅ Secure input handling to prevent SQL injection
✅ Flask-based web UI for ease of use
✅ Automated scanning & report generation

It showcases my ability to write secure Python code, work with APIs, and implement cybersecurity best practices.