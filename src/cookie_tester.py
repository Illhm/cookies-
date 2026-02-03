import requests
import os
import urllib.parse

def fetch_data(source):
    """
    Fetches data from a URL or a local file.
    """
    if source.startswith("http://") or source.startswith("https://"):
        try:
            response = requests.get(source)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
    else:
        if os.path.exists(source):
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print(f"Error: File {source} not found.")
            return None

def parse_netflix_cookies(data):
    """
    Parses the text data to extract Netflix cookies.
    Returns a list of dictionaries, where each dictionary contains cookie data for an account.
    """
    accounts = []
    if not data:
        return accounts

    lines = data.strip().splitlines()
    for line in lines:
        if not line.strip():
            continue

        # Structure is pipe separated
        parts = line.split("|")

        # Extract email/pass from first part usually
        creds = parts[0].strip()

        cookie_data = {}
        # Parse the rest
        for part in parts:
            part = part.strip()
            if "=" in part:
                # Split only on first =
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key in ["NetflixId", "SecureNetflixId"]:
                    cookie_data[key] = value

        if "NetflixId" in cookie_data and "SecureNetflixId" in cookie_data:
            # Associate credentials for identification
            cookie_data["credentials"] = creds
            accounts.append(cookie_data)

    return accounts

def create_cookie_jar(cookie_data):
    """
    Creates a requests CookieJar from the parsed dictionary.
    """
    jar = requests.cookies.RequestsCookieJar()

    # Common attributes for Netflix cookies
    domain = ".netflix.com"
    path = "/"

    if "NetflixId" in cookie_data:
        jar.set("NetflixId", cookie_data["NetflixId"], domain=domain, path=path)

    if "SecureNetflixId" in cookie_data:
        jar.set("SecureNetflixId", cookie_data["SecureNetflixId"], domain=domain, path=path, secure=True)

    return jar

def verify_cookies(cookie_jar):
    """
    Verifies the cookies by making a request to Netflix.
    Returns True if valid (authenticated), False otherwise.
    """
    url = "https://www.netflix.com/browse"
    # User-Agent is often required to avoid immediate blocking or different behavior
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        session = requests.Session()
        session.cookies = cookie_jar
        # We don't want to follow redirects to login page automatically if we want to detect it by 3xx,
        # but usually Netflix redirects to /login or /browse based on auth.
        # Allowing redirects and checking final URL is easier.
        response = session.get(url, headers=headers, timeout=10, allow_redirects=True)

        # If we are at /browse, we are likely authenticated.
        # If we are at /login or / or /de-en/, we might not be.
        # Also check for specific elements in text if possible, but URL check is a good first step.

        if "/browse" in response.url:
            return True

        # Sometimes it redirects to a localized home page if not auth
        if "/login" in response.url:
            return False

        return False

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False
