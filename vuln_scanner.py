import time
import csv
import json
from software_scanner import get_installed_software
from nvd_api import fetch_nvd_vulnerabilities
from tabulate import tabulate

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

def generate_vulnerability_report(vulnerabilities):
    """
    Generates and prints a formatted vulnerability report.
    - Limits descriptions to avoid overflow.
    - Saves the report to CSV and JSON.
    """
    if not vulnerabilities:
        print("\n✅ No known High/Critical vulnerabilities found for installed software.")
        return
    
    print("\n=== 🔥 High & Critical Vulnerability Report 🔥 ===\n")

    # Limit description length for better readability
    formatted_vulnerabilities = [
        [software, version, cve_id, severity, shorten_description(description)]
        for software, version, cve_id, severity, description in vulnerabilities
    ]

    print(tabulate(
        formatted_vulnerabilities, 
        headers=["Software", "Version", "CVE ID", "Severity", "Description"],
        tablefmt="grid"
    ))

    # Export the report
    export_to_csv(vulnerabilities)
    export_to_json(vulnerabilities)

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

if __name__ == "__main__":
    installed_software = get_installed_software()
    vulnerability_results = check_installed_vulnerabilities(installed_software)
    generate_vulnerability_report(vulnerability_results)
