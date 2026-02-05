import json
import os
import zipfile
import shutil

def parse_netscape_cookies(filepath):
    cookies = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) < 7:
                # Malformed line or different format
                # We can log it but for now just skip
                continue

            try:
                domain = parts[0]
                include_subdomains = parts[1].upper() == 'TRUE'
                path = parts[2]
                secure = parts[3].upper() == 'TRUE'
                expiration_raw = int(parts[4])
                name = parts[5]
                value = parts[6]

                # Check if expiration is in milliseconds
                expiration_date = expiration_raw
                if expiration_raw > 100000000000: # > 100 billion
                   expiration_date = expiration_raw / 1000.0

                cookie = {
                    "domain": domain,
                    "hostOnly": not include_subdomains,
                    "path": path,
                    "secure": secure,
                    "expirationDate": expiration_date,
                    "name": name,
                    "value": value,
                    "httpOnly": False,
                    "session": False,
                }

                # Heuristic for HttpOnly
                if name in ['NetflixId', 'SecureNetflixId']:
                     cookie['httpOnly'] = True

                cookies.append(cookie)

            except ValueError:
                continue

    return cookies

def process_data():
    zip_path = "Netflix_85x_7692444028_7CWTkn (1).zip"
    extract_dir = "temp_extracted_process"
    consolidated_file = "tes.txt"
    json_output = "output.json"

    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found.")
        return

    # 1. Extract
    print(f"Extracting {zip_path}...")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # 2. Consolidate
    print(f"Consolidating files to {consolidated_file}...")
    with open(consolidated_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".txt") and "_Netflix_Summary" not in file:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read().strip()
                        if content:
                            outfile.write(content)
                            outfile.write('\n') # Ensure newline between files

    # 3. Convert to JSON
    print(f"Converting {consolidated_file} to {json_output}...")
    cookies = parse_netscape_cookies(consolidated_file)
    print(f"Extracted {len(cookies)} cookies.")

    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=4)

    # 4. Cleanup
    print("Cleaning up...")
    shutil.rmtree(extract_dir)
    print("Done.")

if __name__ == "__main__":
    process_data()
