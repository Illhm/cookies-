import sys
import os
import requests
import requests_mock
import pytest

# Add src to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from cookie_tester import parse_netflix_cookies, create_cookie_jar, verify_cookies

def test_parse_netflix_cookies():
    data = """
    test@example.com:password | Country = US | NetflixId = v%3D3%26ct%3Dval | SecureNetflixId = v%3D3%26mac%3Dval | other = val
    """
    accounts = parse_netflix_cookies(data)
    assert len(accounts) == 1
    assert accounts[0]["credentials"] == "test@example.com:password"
    assert accounts[0]["NetflixId"] == "v%3D3%26ct%3Dval"
    assert accounts[0]["SecureNetflixId"] == "v%3D3%26mac%3Dval"

def test_parse_incomplete_cookies():
    data = """
    test@example.com:password | Country = US | NetflixId = val
    """
    accounts = parse_netflix_cookies(data)
    assert len(accounts) == 0

def test_create_cookie_jar():
    data = {
        "NetflixId": "val1",
        "SecureNetflixId": "val2"
    }
    jar = create_cookie_jar(data)

    # Check if cookies are set
    cookies = jar.get_dict()
    assert cookies["NetflixId"] == "val1"
    assert cookies["SecureNetflixId"] == "val2"

    # Check attributes (requires iterating)
    found = 0
    for cookie in jar:
        if cookie.name == "NetflixId":
            assert cookie.domain == ".netflix.com"
            assert cookie.path == "/"
            found += 1
        if cookie.name == "SecureNetflixId":
            assert cookie.secure == True
            found += 1
    assert found == 2

def test_verify_cookies_valid():
    jar = requests.cookies.RequestsCookieJar()
    with requests_mock.Mocker() as m:
        # Mock browse page
        m.get("https://www.netflix.com/browse", text="<html>... browse ...</html>", status_code=200)

        # In the implementation, verify_cookies checks if response.url contains /browse
        # requests-mock preserves the URL

        assert verify_cookies(jar) is True

def test_verify_cookies_invalid_redirect():
    jar = requests.cookies.RequestsCookieJar()
    with requests_mock.Mocker() as m:
        # Mock redirect to login
        m.get("https://www.netflix.com/browse", headers={"Location": "https://www.netflix.com/login"}, status_code=302)
        m.get("https://www.netflix.com/login", text="Login page", status_code=200)

        assert verify_cookies(jar) is False
