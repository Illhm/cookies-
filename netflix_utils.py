import os

def parse_accounts(filepath):
    """
    Parses a file containing Netflix account information and cookies.

    Args:
        filepath (str): Path to the file to parse.

    Returns:
        list: A list of dictionaries, each containing 'email' and 'cookies'.
    """
    accounts = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return accounts

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

    return accounts
