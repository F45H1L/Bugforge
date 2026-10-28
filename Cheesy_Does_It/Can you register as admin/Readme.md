# Bugforge — Cheesy Does It

## Challenge Overview

- **Challenge:** Cheesy Does It
- **Platform:** Bugforge
- **Category:** Web Security
- **Core Concept:** Unicode NFKC Normalization Desynchronization
- **Objective:** Investigate the application's registration and authorization behavior to retrieve the challenge flag.

## Hint

> Can you register as admin?

The hint suggests that the application may handle usernames inconsistently during registration and authorization. In particular, Unicode compatibility characters may normalize to ordinary ASCII characters, potentially creating a discrepancy between different application components.

## Tools Used

- Browser Developer Tools
- Burp Suite
- Browser Local Storage inspection
- JavaScript source inspection
- HTTP request and response analysis

## Step 1: Inspect the Registration Endpoint

The registration endpoint was identified as:

`POST /api/register`

A registration request was submitted using a username containing fullwidth Unicode characters.

### Request Payload

```json
{
  "username": "\uff41\uff44\uff4d\uff49\uff4e",
  "email": "test3@mail.com",
  "password": "qwerty",
  "full_name": "Test",
  "phone": "1234567890",
  "address": "qwertyuiop,lkjhgfdsa,zxcvbnm"
}
```

The Unicode escape sequences represent the fullwidth username `ａｄｍｉｎ`.

### Response

The server returned HTTP `200 OK` and created the account with ID `7`.

The response preserved the fullwidth username rather than returning the ASCII username `admin`.

This established that registration accepted the Unicode username, but it did not establish that the new account had administrator privileges.

## Step 2: Understand NFKC Normalization

NFKC stands for **Unicode Normalization Form KC**. It performs compatibility decomposition followed by canonical composition.

For example:

```text
Input:       ａｄｍｉｎ
NFKC output: admin
```

The fullwidth Latin characters are compatibility-equivalent to ordinary ASCII letters.

A normalization mismatch can become a security issue if different components validate, store, compare, or authorize usernames using inconsistent representations.

## Step 3: Inspect the Authentication Token

The JWT returned by registration was inspected.

Its decoded payload contained the following information:

```json
{
  "id": 7,
  "username": "ａｄｍｉｎ",
  "iat": 1792685451
}
```

The token preserved the fullwidth username. It did not contain a visible administrator role claim.

Replacing the token in browser Local Storage and refreshing the page did not immediately reveal the flag. This indicated that further investigation of the application's API endpoints was necessary.

**Note:** Decoding a JWT reveals its contents but does not verify its signature or establish the user's actual permissions.

## Step 4: Discover the Admin API Endpoint

The application's JavaScript bundle, `main.js`, was inspected using browser Developer Tools.

Searching the source code for `admin` revealed the following endpoint:

`GET /api/admin/users`

This endpoint appeared to provide access to user records, including usernames and roles.

## Step 5: Send the API Request

The request was sent with the JWT from the registration response in the `Authorization` header.

```http
GET /api/admin/users HTTP/2
Host: lab-1792685028785-a2bdel.labs-app.bugforge.io
Authorization: Bearer <registration-jwt>
```

### Response

The server returned:

- **HTTP status:** `200 OK`
- **Content type:** `application/json`
- **Response data:** A list of user records
- **Flag location:** The `x-flag` HTTP response header

The response contained user records with IDs, usernames, email addresses, profile information, and roles.

Relevant records included:

| ID | Username | Role |
|---:|---|---|
| 1 | `admin` | `admin` |
| 6 | `ADMIN` | `user` |
| 7 | `ａｄｍｉｎ` | `user` |

These records demonstrate that the Unicode username was registered successfully but remained associated with a regular user role.

## Step 6: Retrieve the Flag

The flag was found in the response headers of the successful request to `/api/admin/users`.

```http
x-flag: bug{196NUmdSNF4QetWj8LTAZWNfgohbHzPP}
```

### Flag

```text
bug{196NUmdSNF4QetWj8LTAZWNfgohbHzPP}
```

## Vulnerability Analysis

The challenge hint pointed toward Unicode NFKC normalization desynchronization. The testing established that:

1. The application accepted a fullwidth Unicode username.
2. The registration response and JWT preserved the original Unicode representation.
3. The registered account retained the `user` role.
4. The `/api/admin/users` endpoint returned HTTP 200 when requested with the registration token.
5. The endpoint response exposed the challenge flag in a custom HTTP header.

The successful request demonstrates an apparent authorization weakness. However, the exact root cause cannot be conclusively attributed to NFKC normalization alone without inspecting the backend authorization middleware and username comparison logic.

Possible causes to investigate include inconsistent Unicode normalization, improper role validation, or a missing or incorrect authorization check.

## Security Recommendations

- Normalize usernames consistently before validation, uniqueness checks, storage, and comparison.
- Apply a single, documented username canonicalization policy across the application.
- Never grant administrative privileges solely because a username matches `admin` after normalization.
- Enforce authorization on the server for every administrative API endpoint.
- Retrieve roles from a trusted server-side source and validate permissions on each request.
- Reject or safely handle ambiguous Unicode usernames where appropriate.
- Avoid exposing unnecessary personal information through administrative APIs.
- Add regression tests for Unicode compatibility characters and authorization bypass attempts.

## Conclusion

The Cheesy Does It challenge was solved by investigating Unicode username handling, inspecting the JWT, reviewing the frontend JavaScript for API endpoints, and testing the discovered administrative endpoint.

The decisive finding was that `/api/admin/users` returned the user list and exposed the flag in the `x-flag` response header.

The challenge demonstrates why Unicode normalization, identity handling, and server-side authorization must be implemented consistently.

**Status: Solved**