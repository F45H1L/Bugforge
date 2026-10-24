# CopyPasta — copypasta-010 — Read the snippets.

## Challenge Overview

- **Challenge Name:** CopyPasta
- **Platform:** Bugforge
- **Hint:** Read the snippets.
- **Category:** Web Security
- **Vulnerability:** Filter Operator Injection / Broken Access Control
- **Status:** Solved

## 1. Objective

The objective was to investigate the CopyPasta snippet-sharing application and retrieve the challenge flag by exploiting a vulnerability in its public snippet search API.

The challenge hint was:

> Read the snippets.

## 2. Initial Reconnaissance

After registering a test user and logging in, I navigated to the **Public Snippets** section.

I discovered a snippet titled **CopyPasta search API — notes**, published by `coder123`.

The snippet documented the following API endpoint:

```http
GET /api/snippets/public?search=<text>&language=<lang>
```

It also described advanced field filtering:

```http
GET /api/snippets/public?filter[language]=python
GET /api/snippets/public?filter[title]=Fetch API Helper
```

The snippet claimed that the endpoint only returned snippets marked as public.

This documentation provided a potential attack surface: user-controlled filters might allow access to records that should remain private.

## 3. Testing the API

The challenge API was hosted at:

```text
https://lab-1792848894893-3aoz7s.labs-app.bugforge.io
```

I used browser Developer Tools and inspected the requests and responses. I then tested the filter functionality using Burp Suite.

### Initial request

I tested the documented filtering behavior using a request such as:

```http
GET /api/snippets/public?filter[title]=Fetch%20API%20Helper
```

The API returned public snippet records, confirming that the filter endpoint was operational.

### Testing alternative field names

I attempted variations using different visibility field names and a not-equal operator.

These attempts did not expose private snippets:

```http
GET /api/snippets/public?filter[isPublic][$ne]=true
```

```http
GET /api/snippets/public?filter[is_Public][$ne]=true
```

The responses continued to contain public snippets only.

This suggested that the field name and value type were important.

## 4. Exploitation

After examining the JSON responses, I identified the actual visibility field:

```json
{
  "is_public": 1
}
```

The field was named `is_public`, and its value was represented numerically.

I modified the filter to use the `$ne` (not equal) operator.

### Successful request

```http
GET /api/snippets/public?filter[is_public][$ne]=1
```

**HTTP status:** `200 OK`

### Result

The response contained snippets whose visibility field was set to `0`, despite the endpoint being documented as public-only.

Two notable records were exposed:

| Snippet ID | Title | Owner | Visibility |
|---|---|---|---|
| 9 | infra runbook (private) | admin | Private |
| 4 | Password Generator | pythonista | Private |

The returned JSON included a `flag` field in the exposed private records.

This confirmed that the public snippet search endpoint could be manipulated to return private data.

## 5. Flag

The challenge flag was:

```text
bug{L7uFOozVRFtdLOGbJqMitT23eijbDEv4}
```

## 6. Vulnerability Analysis

The observed behavior is consistent with **filter operator injection combined with broken access control**.

The API accepted a nested filter parameter:

```text
filter[is_public][$ne]=1
```

The `$ne` operator represented a not-equal condition. Instead of restricting the result set to public snippets, the API returned records whose `is_public` value was not `1`.

The likely underlying issue is that the server allowed user-controlled filters to influence the database query without independently enforcing the public visibility restriction.

The exact database technology and internal query implementation were not confirmed from the HTTP responses alone.

## 7. Root Cause

The endpoint appears to rely on client-controlled filtering to determine which records are returned.

A secure implementation must enforce the visibility condition on the server, regardless of the filters supplied by the client.

Additional weaknesses may include:

- Accepting nested query operators without validation.
- Allowing filters on sensitive fields.
- Failing to enforce record-level access controls.
- Returning sensitive fields, such as the challenge flag, in API responses.

## 8. Recommended Remediation

### Enforce public visibility server-side

The backend should always restrict this endpoint to public snippets before applying optional search filters.

For a SQL-backed implementation, the query could follow this pattern:

```sql
SELECT id, title, code, language, description
FROM snippets
WHERE is_public = 1;
```

Additional search conditions should be combined with this mandatory visibility condition.

### Allowlist filter fields

Only explicitly supported fields should be accepted from user input, such as:

- `title`
- `language`

Sensitive fields such as `is_public`, internal identifiers, ownership data, and privileged metadata should not be freely filterable through the public endpoint.

### Validate operators and values

Reject unsupported nested operators and validate the expected type of every filter value.

### Apply authorization before serialization

The backend must authorize access to each record before returning it. It should also omit sensitive properties that the requesting user is not allowed to see.

## 9. Lessons Learned

- Public API documentation can reveal useful attack surfaces.
- Client-controlled filters must not override server-side authorization.
- Exact field names and value types matter when testing injection vulnerabilities.
- HTTP `200 OK` does not mean that access controls are working correctly.
- Always inspect the complete JSON response for unexpected records and sensitive fields.
- An observed `$ne` operator does not, by itself, prove that the application uses MongoDB.

## 10. Conclusion

The CopyPasta challenge was solved by examining the public snippet documentation, testing the advanced filter functionality, identifying the actual `is_public` field, and supplying a not-equal filter.

The successful request exposed private snippets and revealed the challenge flag.

**Final outcome:** Challenge solved; flag recovered.