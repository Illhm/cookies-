# Netflix Cookie Tester

A robust Python tool to parse, manage, and verify Netflix authentication cookies from a specific data format.

## Features

- **Fetching**: Retrieves cookie data from a URL or local file.
- **Parsing**: Extracts `NetflixId` and `SecureNetflixId` from the custom pipe-separated format.
- **Verification**: Verifies the cookies by making a request to Netflix's browse page.
- **Output**: Generates a JSON report of valid and invalid accounts.

## Prerequisites

- Python 3.6+
- `requests` library

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Usage

Fetch cookies from the default URL and output to stdout:

```bash
python main.py
```

### verify Cookies

Fetch cookies and verify if they are still active:

```bash
python main.py --verify
```

### Custom Source

Fetch cookies from a local file or different URL:

```bash
python main.py --source p.txt --verify
```

### Save Output

Save the results to a JSON file:

```bash
python main.py --verify --output results.json
```

## Data Format

The tool expects a text file where each line represents an account in the following format:

```text
email:password | Key = Value | NetflixId = ... | SecureNetflixId = ... | ...
```

It specifically looks for `NetflixId` and `SecureNetflixId`.

## Security & Privacy Note

**IMPORTANT**: This tool handles sensitive authentication cookies that provide access to user accounts.

- **Do not share** output files containing valid cookies.
- **Do not use** this tool on data you do not have permission to access.
- This tool is for educational and testing purposes only.

## Methodology

The tool works by:
1.  Parsing the input text to extract cookie values.
2.  Constructing a `requests.CookieJar` with the correct domain (`.netflix.com`) and flags (`Secure`, `HttpOnly`).
3.  Sending a GET request to `https://www.netflix.com/browse`.
4.  Analyzing the final URL and response to determine if the session is authenticated (valid) or redirected to a login page (invalid).
