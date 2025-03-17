import requests

def fetch_nvd_vulnerabilities(software_name):
    """
    Queries the NVD API (version 2.0) for vulnerabilities related to the given software name.
    Returns a list of vulnerability details.
    """
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={software_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an error if the request fails
        data = response.json()
        
        vulnerabilities = []
        for item in data.get("vulnerabilities", []):
            cve_id = item["cve"]["id"]
            description = item["cve"]["descriptions"][0]["value"]
            vulnerabilities.append({"cve_id": cve_id, "description": description})
        
        return vulnerabilities

    except requests.exceptions.RequestException as e:
        print(f"Error fetching vulnerabilities from NVD: {e}")
        return []

# Test the function
if __name__ == "__main__":
    software_name = "Python"  # Example software name
    vulnerabilities = fetch_nvd_vulnerabilities(software_name)

    if vulnerabilities:
        print(f"\nVulnerabilities for {software_name}:")
        for vuln in vulnerabilities[:5]:  # Show first 5 vulnerabilities
            print(f"[{vuln['cve_id']}] - {vuln['description']}")
    else:
        print(f"No vulnerabilities found for {software_name}.")
