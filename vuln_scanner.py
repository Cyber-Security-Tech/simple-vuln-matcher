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

    for software in software_list[:10]:  # Limit to first 10 items for testing
        name = software["name"]
        version = software["version"]
        print(f"Checking {name} {version}...")  # Show progress

        vulnerabilities = fetch_nvd_vulnerabilities(name)
        if vulnerabilities:
            for vuln in vulnerabilities:
                results.append([name, version, vuln["cve_id"], vuln["description"]])

    return results

def generate_vulnerability_report(vulnerabilities):
    """
    Generates and prints a formatted vulnerability report.
    - Limits descriptions to avoid overflow.
    - Uses tabulate to make output structured.
    """
    if not vulnerabilities:
        print("\n✅ No known vulnerabilities found for installed software.")
        return

    print("\n=== 🔥 Vulnerability Report 🔥 ===\n")

    # Limit description length for better readability
    formatted_vulnerabilities = [
        [software, version, cve_id, shorten_description(description)]
        for software, version, cve_id, description in vulnerabilities
    ]

    print(tabulate(
        formatted_vulnerabilities, 
        headers=["Software", "Version", "CVE ID", "Description"],
        tablefmt="grid"
    ))

if __name__ == "__main__":
    installed_software = get_installed_software()
    vulnerability_results = check_installed_vulnerabilities(installed_software)
    generate_vulnerability_report(vulnerability_results)
