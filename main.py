import argparse
import os
import sys
import asyncio
from cookie_tester import verify_account_async
from netflix_utils import parse_accounts

async def run_checks(args):
    # Mode 1: Batch file processing
    filepath = args.file
    # Auto-detect p.txt if no args provided
    if not filepath and not args.cookie and os.path.exists('p.txt'):
        # Check if user meant to run without args to use p.txt
        # If args.url is present, we ignore it basically, or treat it as single mode?
        # The original code logic: if not filepath and not args.url and exists('p.txt') -> use p.txt
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
                 print(f"[+] {email}: Success")
                 for line in result:
                     print(f"    {line}")
                 print("-" * 40)
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
            for line in result:
                print(line)
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

    args = parser.parse_args()

    asyncio.run(run_checks(args))

if __name__ == "__main__":
    main()
