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
    """Fetch vulnerabilities from NVD API based on software name."""
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    # Add API key to request headers
    headers = {
        "apiKey": API_KEY
    }
    
    software_name = clean_software_name(software_name)  # Clean the software name

    params = {
        "keywordSearch": software_name,
        "resultsPerPage": 10  # Limit results to 10 per software
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)

        data = response.json()

        if "vulnerabilities" in data:
            return [
                {
                    "cve_id": vuln["cve"]["id"],
                    "description": vuln["cve"]["descriptions"][0]["value"]
                }
                for vuln in data["vulnerabilities"]
            ]
        else:
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching vulnerabilities from NVD: {e}")
        return []
