import subprocess

def get_installed_software():
    """
    Scans and retrieves a list of installed software and their versions.
    Works on Windows using PowerShell or WMIC.
    Returns a list of dictionaries with 'name' and 'version' keys.
    """
    try:
        # Try PowerShell (preferred method)
        cmd = 'powershell "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion"'
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        software_list = []

        for line in output.stdout.split("\n"):
            if line.strip() and "DisplayName" not in line and "------" not in line:
                parts = line.strip().split("  ")
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) == 2:
                    software_list.append({"name": parts[0], "version": parts[1]})
                elif len(parts) == 1:
                    software_list.append({"name": parts[0], "version": "Unknown"})

        if not software_list:
            print("PowerShell method failed. Trying WMIC...")

            # Try WMIC as a fallback (deprecated but still works)
            cmd = 'wmic product get name,version'
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = output.stdout.split("\n")[1:]  # Skip the first line (header)

            for line in lines:
                parts = line.strip().split("  ")
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) >= 2:
                    software_list.append({"name": parts[0], "version": parts[1]})
                elif len(parts) == 1:
                    software_list.append({"name": parts[0], "version": "Unknown"})

        return software_list

    except Exception as e:
        print(f"Error fetching installed software: {e}")
        return []

# Test the function
if __name__ == "__main__":
    installed_software = get_installed_software()
    for software in installed_software[:10]:  # Print first 10 results
        print(f"{software['name']} - {software['version']}")
