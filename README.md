# Cookie Tester

This tool allows you to test HTTP cookies against a target URL, either individually or in batch from a file. It is specifically optimized to handle Netflix account cookies found in common formats.

## Installation

1. Install Python 3.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Batch Testing (Netflix)

To test a list of accounts/cookies from a file:

```bash
python3 main.py --file p.txt
```

If `p.txt` exists in the current directory and no arguments are provided, it will be used by default:

```bash
python3 main.py
```

**File Format (`p.txt`):**
The tool expects lines in the following format (pipe-delimited):
```
email:password | Country = ... | NetflixId = ... | SecureNetflixId = ...
```

### Single Cookie Testing

Run the script with a specific URL and cookie:

```bash
python3 main.py --url <TARGET_URL> --cookie "<COOKIE_NAME>=<COOKIE_VALUE>"
```

**Example:**

```bash
python3 main.py --url https://httpbin.org/cookies --cookie "session_id=12345"
```

## Disclaimer

**Educational Use Only.** This tool is intended for testing and debugging cookies for accounts you own or have explicit permission to test. Unauthorized use of cookies or account information is a violation of terms of service and potentially illegal.
