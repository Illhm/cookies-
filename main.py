import argparse
from cookie_tester import test_cookie

def main():
    parser = argparse.ArgumentParser(description="Test cookies against a URL.")
    parser.add_argument("--url", required=True, help="The target URL.")
    parser.add_argument("--cookie", required=True, help="Cookie in 'name=value' format.")

    args = parser.parse_args()

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
        print("Response Body:")
        print(response.text)
    else:
        print("Failed to get a response.")

if __name__ == "__main__":
    main()
