import requests
import time

# 🔒 Replace with your actual NVD API key (KEEP IT PRIVATE!)
API_KEY = "3f71c4da-ea43-4eaa-a9fd-85668036d87d"

def clean_software_name(name):
    """Normalize software names for better NVD API searches."""
    name = name.lower()
    name = name.replace("(x64)", "").replace("(64-bit)", "").replace("(32-bit)", "")
    name = name.replace("-", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    name = name.strip()
    
    # Use only the first part of the name
    name_parts = name.split()
    if len(name_parts) > 1:
        name = name_parts[0]  # Keep only the first word
    
    return name

def fetch_nvd_vulnerabilities(software_name):
    """Fetch vulnerabilities from NVD API based on software name and filter by severity."""
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    headers = {"apiKey": API_KEY}
    
    software_name = clean_software_name(software_name)  # Normalize name

    params = {
        "keywordSearch": software_name,
        "resultsPerPage": 50  # Fetch more results to ensure we capture High/Critical vulnerabilities
    }

    try:
        print(f"Requesting NVD API: {base_url} with params: {params}")

        response = requests.get(base_url, headers=headers, params=params)
       

        response.raise_for_status()
         print(f"Received API Response: {response.status_code}")
        data = response.json()

        filtered_vulnerabilities = []
        
        if "vulnerabilities" in data:
            for vuln in data["vulnerabilities"]:
                cve_id = vuln["cve"]["id"]
                description = vuln["cve"]["descriptions"][0]["value"]
                
                # Get CVSS Severity (Critical, High, Medium, Low)
                severity = "UNKNOWN"
                if "metrics" in vuln["cve"]:
                    if "cvssMetricV31" in vuln["cve"]["metrics"]:  
                        severity = vuln["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseSeverity"]
                    elif "cvssMetricV30" in vuln["cve"]["metrics"]:  
                        severity = vuln["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["baseSeverity"]

                # **Only include High/Critical vulnerabilities**
                if severity in ["HIGH", "CRITICAL"]:
                    filtered_vulnerabilities.append({
                        "cve_id": cve_id,
                        "severity": severity,
                        "description": description
                    })

        return filtered_vulnerabilities

    except requests.exceptions.RequestException as e:
        print(f"Error fetching vulnerabilities from NVD: {e}")
        return []
