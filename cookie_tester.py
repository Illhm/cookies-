import requests

def test_cookie(url, cookie_data):
    """
    Tests if cookies are accepted by the target URL.

    Args:
        url (str): The target URL.
        cookie_data (dict): A dictionary of cookies to send.

    Returns:
        requests.Response: The response object.
    """
    session = requests.Session()
    session.cookies.update(cookie_data)
    try:
        response = session.get(url, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return None
