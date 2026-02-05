# Assumptions and Parsing Logic

## Input Format
The input files extracted from the ZIP archive were assumed to be in the **Netscape HTTP Cookie File** format (tab-separated values).
The columns were interpreted as follows:
1.  **Domain**: The domain that created the cookie.
2.  **Include Subdomains**: Boolean-like flag (TRUE/FALSE).
3.  **Path**: The path within the domain for which the cookie is valid.
4.  **Secure**: Boolean-like flag (TRUE/FALSE) indicating if a secure connection is required.
5.  **Expiration**: Unix timestamp.
6.  **Name**: The name of the cookie.
7.  **Value**: The value of the cookie.

## parsing Logic & JSON Conversion

### 1. Expiration Date
- The input timestamps appeared to be in varying formats (seconds vs milliseconds).
- Logic was applied to detect millisecond timestamps (values > 100,000,000,000) and convert them to seconds to maintain consistency with standard JSON cookie formats (like EditThisCookie).

### 2. HostOnly Flag
- The `hostOnly` attribute in the JSON output is derived from the "Include Subdomains" column in the Netscape format.
- If "Include Subdomains" is `TRUE`, `hostOnly` is set to `false`.
- If "Include Subdomains" is `FALSE`, `hostOnly` is set to `true`.

### 3. HttpOnly Flag
- The Netscape format does not explicitly store the `HttpOnly` flag.
- A heuristic was applied: Cookies named `NetflixId` and `SecureNetflixId` are assumed to be `HttpOnly` (`httpOnly: true`).
- All other cookies default to `httpOnly: false` unless otherwise specified by updated logic.

### 4. Session Cookies
- Since all cookies in the input file had expiration dates, `session` is set to `false` for all entries.

### 5. Output Format
- The data is consolidated into a single JSON array containing cookie objects.
- The schema is compatible with the **EditThisCookie** extension format.
