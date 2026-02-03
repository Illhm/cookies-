import requests

def test_cookie(url, cookie_data, headers=None):
    """
    Tests if cookies are accepted by the target URL.

    Args:
        url (str): The target URL.
        cookie_data (dict): A dictionary of cookies to send.
        headers (dict, optional): Additional headers to send.

    Returns:
        requests.Response: The response object.
    """
    session = requests.Session()

    # Default headers to mimic a real browser
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    if headers:
        default_headers.update(headers)

    session.headers.update(default_headers)

    # Set cookies with specific domain if needed, otherwise generic set
    # We assume cookie_data contains name:value pairs.
    # For Netflix, it is crucial to set them for .netflix.com if possible,
    # but requests.Session() usually handles simple dicts by setting them on the request.
    # To be more robust for domain matching:
    if '.netflix.com' in url or 'netflix.com' in url:
        for name, value in cookie_data.items():
            session.cookies.set(name, value, domain='.netflix.com', path='/')
    else:
        session.cookies.update(cookie_data)

    try:
        response = session.get(url, timeout=10, allow_redirects=True)
        return response
    except requests.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return None
