import os
import json

def parse_json_dump(filepath):
    """
    Parses a JSON file containing a list of cookies (EditThisCookie format).
    Groups cookies into sessions based on 'NetflixId' changes.
    """
    accounts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cookie_list = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return accounts

    current_cookies = {}

    for cookie in cookie_list:
        name = cookie.get('name')
        value = cookie.get('value')

        if not name or not value:
            continue

        # If we encounter a duplicate critical cookie that differs from what we have,
        # it implies a new session.
        if name in ['NetflixId', 'SecureNetflixId']:
            if name in current_cookies and current_cookies[name] != value:
                # Flush current session
                if 'NetflixId' in current_cookies or 'SecureNetflixId' in current_cookies:
                    accounts.append({'email': 'Unknown', 'cookies': current_cookies})

                # Start new session
                current_cookies = {}

        current_cookies[name] = value

    # Flush last session
    if 'NetflixId' in current_cookies or 'SecureNetflixId' in current_cookies:
        accounts.append({'email': 'Unknown', 'cookies': current_cookies})

    return accounts

def parse_netscape_dump(filepath):
    """
    Parses a Netscape HTTP Cookie file.
    Groups cookies into sessions based on 'NetflixId' changes.
    """
    accounts = []
    current_cookies = {}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split('\t')
                if len(parts) < 7:
                    continue

                name = parts[5]
                value = parts[6]

                if name in ['NetflixId', 'SecureNetflixId']:
                    if name in current_cookies and current_cookies[name] != value:
                        if 'NetflixId' in current_cookies or 'SecureNetflixId' in current_cookies:
                             accounts.append({'email': 'Unknown', 'cookies': current_cookies})
                        current_cookies = {}

                current_cookies[name] = value

        # Flush last session
        if 'NetflixId' in current_cookies or 'SecureNetflixId' in current_cookies:
            accounts.append({'email': 'Unknown', 'cookies': current_cookies})

    except Exception as e:
        print(f"Error reading Netscape file: {e}")

    return accounts

def parse_pipe_delimited(filepath):
    """
    Parses the legacy pipe-delimited format.
    """
    accounts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(' | ')
                account_data = {}
                cookies = {}

                # Extract email/pass from the first part
                first_part = parts[0]
                if ':' in first_part:
                    account_data['email'] = first_part.split(':')[0]
                else:
                    account_data['email'] = "Unknown"

                for part in parts:
                    if ' = ' in part:
                        key, value = part.split(' = ', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'NetflixId':
                            cookies['NetflixId'] = value
                        elif key == 'SecureNetflixId':
                            cookies['SecureNetflixId'] = value

                if 'NetflixId' in cookies or 'SecureNetflixId' in cookies:
                    account_data['cookies'] = cookies
                    accounts.append(account_data)
    except Exception as e:
         print(f"Error reading pipe-delimited file: {e}")

    return accounts

def parse_accounts(filepath):
    """
    Parses a file containing Netflix account information and cookies.
    Detects format based on extension and content.

    Args:
        filepath (str): Path to the file to parse.

    Returns:
        list: A list of dictionaries, each containing 'email' and 'cookies'.
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []

    # 1. JSON Check
    if filepath.lower().endswith('.json'):
        return parse_json_dump(filepath)

    # 2. Content Check
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()

        # Check for Netscape signature (tabs, usually 7 fields, or # Netscape)
        # Typical line: .netflix.com	TRUE	/	FALSE	123456	name	value
        if '\t' in first_line and len(first_line.split('\t')) >= 7:
            return parse_netscape_dump(filepath)
        elif first_line.startswith('#'):
             # Could be comment header
             return parse_netscape_dump(filepath)

    except Exception:
        pass

    # 3. Fallback to Pipe Delimited
    return parse_pipe_delimited(filepath)

def extract_netflix_account_info(html):
    """
    Placeholder for extracting Netflix account info.
    The actual scraping logic is handled by regexes in cookie_tester.py,
    but the snippet calls this function.

    Args:
        html (str): The HTML content.

    Returns:
        str: Extracted info string or None.
    """
    # TODO: Implement actual extraction if needed.
    # For now, return None so the calling code handles it (empty billed_using list).
    return None
