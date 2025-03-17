import time
import csv
import json
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
    """
    Checks each installed software for vulnerabilities using the NVD API.
    Returns a list of matched vulnerabilities.
    """
    results = []
    print("\nScanning installed software for vulnerabilities...\n")

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
        writer.writerow(["Software", "Version", "CVE ID", "Severity", "Description"])  # Header
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
    """Exports vulnerabilities to a formatted PDF with proper text wrapping, spacing, and no header overlap."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    def add_page_header():
        """Adds a header at the top of each new page."""
        c.drawString(200, 750, "Vulnerability Report (Continued)")
        c.drawString(200, 735, "-------------------------------------------")
        return 720  # Start vulnerabilities lower to prevent overlap

    c.drawString(200, 750, "Vulnerability Report (High & Critical Only)")
    c.drawString(200, 735, "-------------------------------------------")

    y_position = 720
    max_width = 500  # Maximum width for text wrapping
    line_height = 15  # Height of each line of text

    for software, version, cve_id, severity, description in vulnerabilities:
        if y_position < 150:  # Start a new page if space runs out
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = add_page_header()  # Add header and reset y_position

        c.drawString(50, y_position, f"Software: {software} ({version})")
        y_position -= line_height
        c.drawString(50, y_position, f"CVE ID: {cve_id} | Severity: {severity}")
        y_position -= line_height

        # Wrap the description text dynamically
        wrapped_description = simpleSplit(description, "Helvetica", 12, max_width)
        for line in wrapped_description:
            c.drawString(50, y_position, line)
            y_position -= line_height  # Move down for next line

        # Add extra spacing after each entry to prevent overlap
        y_position -= 20
        c.drawString(50, y_position, "-" * 90)
        y_position -= 20  # Extra space before next entry

    c.save()
    print(f"\n📂 Report saved as {filename}")

def export_to_html(vulnerabilities, filename="vulnerabilities_report.html"):
    """Exports vulnerabilities to an HTML file."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vulnerability Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { color: #d9534f; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>Vulnerability Report (High & Critical Only)</h2>
        <table>
            <tr>
                <th>Software</th>
                <th>Version</th>
                <th>CVE ID</th>
                <th>Severity</th>
                <th>Description</th>
            </tr>
            {% for software, version, cve_id, severity, description in vulnerabilities %}
            <tr>
                <td>{{ software }}</td>
                <td>{{ version }}</td>
                <td>{{ cve_id }}</td>
                <td style="color: {% if severity == 'CRITICAL' %}red{% else %}orange{% endif %};">
                    {{ severity }}
                </td>
                <td>{{ description[:100] }}...</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_output = template.render(vulnerabilities=vulnerabilities)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_output)

    print(f"\n📂 Report saved as {filename}")

def generate_vulnerability_report(vulnerabilities):
    """
    Generates and prints a formatted vulnerability report.
    - Limits descriptions to avoid overflow.
    - Saves the report to CSV, JSON, PDF, and HTML.
    """
    if not vulnerabilities:
        print("\n✅ No known High/Critical vulnerabilities found for installed software.")
        return
    
    print("\n=== 🔥 High & Critical Vulnerability Report 🔥 ===\n")

    formatted_vulnerabilities = [
        [software, version, cve_id, severity, shorten_description(description)]
        for software, version, cve_id, severity, description in vulnerabilities
    ]

    print(tabulate(
        formatted_vulnerabilities, 
        headers=["Software", "Version", "CVE ID", "Severity", "Description"],
        tablefmt="grid"
    ))

    # Export the report in different formats
    export_to_csv(vulnerabilities)
    export_to_json(vulnerabilities)
    export_to_pdf(vulnerabilities)
    export_to_html(vulnerabilities)

if __name__ == "__main__":
    installed_software = get_installed_software()
    vulnerability_results = check_installed_vulnerabilities(installed_software)
    generate_vulnerability_report(vulnerability_results)
