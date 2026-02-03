# Cookie Tester

This is a simple tool to test cookies against a target URL.

## Installation

1. Install Python 3.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with the URL and the cookie you want to test.

```bash
python3 main.py --url <TARGET_URL> --cookie "<COOKIE_NAME>=<COOKIE_VALUE>"
```

### Example

Test a cookie against httpbin.org (a safe testing service):

```bash
python3 main.py --url https://httpbin.org/cookies --cookie "session_id=12345"
```

This will send a request to `https://httpbin.org/cookies` with the cookie `session_id=12345`. The response body should show the cookie that was received by the server.
