🔐 Task #14 — Two-Factor Authentication (2FA) System
💡 Description:

You’re building an authentication layer for highly secure users. Add support for Two-Factor Authentication using email-based codes (no actual emails need to be sent — simulate it).

📌 Functional Requirements
✅ 1. Registration

Same as before (username, password, etc.)
Add a new field: enable_2fa: bool
If enable_2fa = True, require a second login step after password validation.
✅ 2. Login (Step 1)

Validate username/password.
If 2FA is enabled, return {"message": "2FA required"} and generate a random 6-digit code.
Store the code in memory (db["2fa_codes"]) with an expiry of 2 minutes.
✅ 3. Login (Step 2)

POST to /2fa/verify with:
{
  "username": "andrii",
  "code": "123456"
}
If correct and not expired → issue JWT token.
✅ 4. Normal Users (no 2FA)

Authenticate as usual, direct token response from /token.