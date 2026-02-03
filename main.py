import argparse
import os
import sys
from cookie_tester import test_cookie
from netflix_utils import parse_accounts

def main():
    parser = argparse.ArgumentParser(description="Test cookies against a URL.")
    parser.add_argument("--url", help="The target URL.")
    parser.add_argument("--cookie", help="Cookie in 'name=value' format.")
    parser.add_argument("--file", help="Path to a file containing account/cookie data.")

    args = parser.parse_args()

    # Mode 1: Batch file processing
    filepath = args.file
    if not filepath and not args.url and os.path.exists('p.txt'):
        filepath = 'p.txt'
        print("No arguments provided. Defaulting to 'p.txt'.")

    if filepath:
        print(f"Reading accounts from {filepath}...")
        accounts = parse_accounts(filepath)
        print(f"Found {len(accounts)} accounts.")

        target_url = args.url if args.url else "https://www.netflix.com/browse"

        print(f"Testing against {target_url}...\n")

        for acc in accounts:
            email = acc.get('email', 'Unknown')
            cookies = acc.get('cookies', {})

            if not cookies:
                print(f"[-] {email}: No valid cookies found.")
                continue

            response = test_cookie(target_url, cookies)

            if response:
                status = response.status_code
                # Netflix often redirects to /login if cookies are invalid, or returns 200 on success.
                # However, bot protection might return 403 or 405 or 5xx.
                if status == 200:
                    if "browse" in response.url:
                         print(f"[+] {email}: Success (200) - Redirected to Browse")
                    else:
                         print(f"[+] {email}: Success (200) - URL: {response.url}")
                elif status in [301, 302, 307]:
                     print(f"[*] {email}: Redirect ({status}) -> {response.headers.get('Location')}")
                else:
                    print(f"[-] {email}: Failed ({status})")
            else:
                print(f"[-] {email}: Connection Error")
        return

    # Mode 2: Single cookie testing
    if args.url and args.cookie:
        try:
            key, value = args.cookie.split('=', 1)
            cookie_data = {key: value}
        except ValueError:
            print("Error: Cookie must be in 'name=value' format.")
            return

        print(f"Testing cookie '{args.cookie}' against {args.url}...")
        response = test_cookie(args.url, cookie_data)

        if response:
            print(f"Status Code: {response.status_code}")
            print("Response Body Snippet (first 500 chars):")
            print(response.text[:500])
        else:
            print("Failed to get a response.")
        return

    # Fallback if arguments are missing
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    main()
