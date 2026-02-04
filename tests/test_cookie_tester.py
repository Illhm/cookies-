import pytest
import respx
from httpx import Response
from cookie_tester import verify_account_async

# Removed space in "value": true} to match regex expectation
# Removed space in "value":1609459200000 to match regex expectation for memberSince
SAMPLE_HTML = """
<html>
<script>
window.netflix = {
    "canChangePlan": { "fieldType": "Boolean", "value": true},
    "isUserOnHold": false,
    "localizedPlanName": { "fieldType": "String", "value": "Premium Ultra HD" },
    "membershipStatus": "CURRENT_MEMBER",
    "countryOfSignup": "US",
    "firstName": "John",
    "emailAddress": "john.doe@example.com",
    "phoneNumber": "555-0199",
    "memberSince": { "fieldType": "Date", "value":1609459200000 },
    "nextBillingDate": { "fieldType": "Date", "value": "February 20, 2025" },
    "showExtraMemberSection": { "fieldType": "Boolean", "value": false },
    "language": "en"
};
</script>
</html>
"""

@pytest.mark.asyncio
async def test_verify_account_success():
    async with respx.mock:
        # Specific mocks first
        respx.get("https://www.netflix.com/account").respond(200, text=SAMPLE_HTML)
        respx.get("https://www.netflix.com").respond(200)

        cookies = {"NetflixId": "dummy", "SecureNetflixId": "dummy"}
        result = await verify_account_async(cookies)

        assert result is not None
        assert isinstance(result, dict)
        assert "lines" in result
        assert "cookies" in result
        assert "info" in result

        assert result["info"]["region"] == "US"
        assert result["info"]["next_billing_date"] == "February 20, 2025"

        lines = result["lines"]
        result_text = "\n".join(lines)

        assert "Account Information:" in lines
        assert "Country: (US) United States" in result_text
        assert "Membership status: Current Member" in result_text
        assert "Plan status: Active" in result_text
        assert "Plan details: Premium Ultra HD" in result_text
        assert "Can change plan: True" in result_text
        assert "Next payment: February 20, 2025" in result_text
        assert "Signup D&T: Jan 1, 2021 at 00:00:00 UTC" in result_text
        assert "Extra Slots: False" in result_text
        assert "Mail: john.doe@example.com" in result_text
        assert "Phone: 555-0199" in result_text
        assert "Name: John" in result_text
        assert "Display Language: English" in result_text
        assert "✅ This cookie is working, enjoy Netflix 🍿" in result_text

@pytest.mark.asyncio
async def test_verify_account_failure():
    async with respx.mock:
        # Specific mocks first
        respx.get("https://www.netflix.com/login").respond(200, text="Login Page")
        respx.get("https://www.netflix.com/account").respond(
            302, headers={"Location": "https://www.netflix.com/login"}
        )
        respx.get("https://www.netflix.com").respond(200)

        cookies = {"NetflixId": "dummy"}
        result = await verify_account_async(cookies)

        assert result is None
