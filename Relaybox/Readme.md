# Relaybox — relaybox-003 — Compare the search response with what the article page lets a customer read.

## Overview

**Challenge:** Relaybox
**Platform:** Bugforge
**Vulnerability:** Sensitive Information Disclosure
**Affected Endpoint:** `/api/articles/suggest`
**Difficulty:** Based on the challenge environment

### Challenge Hint

> Compare the search response with what the article page lets a customer read.

The hint indicates that the article search functionality may disclose information that should not be available to ordinary customers.

## 1. Initial Reconnaissance

I opened the Relaybox web application and created a test customer account. After logging in, I navigated to the Help Centre, which displayed several knowledge-base articles.

I opened Firefox Developer Tools and selected the **Network** tab to inspect the application's API requests and responses.

## 2. Inspecting the Articles API

When the Help Centre loaded, the application made the following request:

```http
GET /api/articles HTTP/2
Host: lab-1792601359673-ui5nrv.labs-app.bugforge.io
```

The server returned a JSON array containing article information.

Example response structure:

```json
{
  "id": "e0ab8e30-b9c6-4b51-94a8-9ba32a3b404b",
  "workspace_id": "northstar",
  "title": "Bring your projects with you",
  "category": "Getting started",
  "body": "You can import a project from a CSV file...",
  "published": 1,
  "updated_at": "2026-10-21T16:49:20.289Z"
}
```

The response contained article identifiers, workspace information, titles, categories, full article bodies, publication status, and update timestamps.

The articles returned in this initial response were published.

## 3. Inspecting the Search Functionality

The Help Centre provided a search feature. I searched for the keyword `Bring` and inspected the resulting network request.

The application made the following request:

```http
GET /api/articles/suggest?q=Bring HTTP/2
Host: lab-1792601359673-ui5nrv.labs-app.bugforge.io
```

The response contained matching articles with their IDs, titles, categories, excerpts, and publication status.

Example:

```json
{
  "id": "e0ab8e30-b9c6-4b51-94a8-9ba32a3b404b",
  "title": "Bring your projects with you",
  "category": "Getting started",
  "excerpt": "You can import a project from a CSV file...",
  "published": 1
}
```

At this point, the search response appeared normal. However, the challenge hint suggested comparing what the search endpoint returned with what customers could access through the article interface.

## 4. Discovering the Information Disclosure

I searched for the keyword `Bug` and inspected the JSON response from the search endpoint.

This time, the server returned an unpublished article:

```json
[
  {
    "id": "429d1484-7070-47d7-8a53-7cdb872773a9",
    "title": "Invite delivery checks",
    "category": "Account",
    "excerpt": "When a team invitation does not arrive, support can use the private escalation code bug{LccLBPNmmkVtyoZmvlIxDdzSXeLp1hYf} to review the delivery trace. Keep this procedure inside the support team.",
    "published": 0
  }
]
```

This was the important discovery.

The response explicitly marked the article as unpublished:

```json
"published": 0
```

Despite this, the search endpoint returned the article's title, category, and excerpt to the customer. The excerpt also contained information explicitly described as private and intended for the support team.

### Recovered Secret

```text
bug{LccLBPNmmkVtyoZmvlIxDdzSXeLp1hYf}
```

The value was recovered directly from the search API response.

## 5. Understanding the Vulnerability

The likely vulnerability is **sensitive information disclosure through improper filtering of unpublished articles**.

The search endpoint appears to return an unpublished article when its content matches the supplied search term.

The issue is not simply that the API returns JSON. The concern is that content intended for internal support use is exposed to a customer account through the search functionality.

### Expected Behaviour

The server should return only articles that the authenticated customer is authorized to read. Unpublished or internal support articles should not appear in customer-facing search results.

### Observed Behaviour

The search endpoint returned an article with:

```json
"published": 0
```

Its excerpt contained a private escalation code and instructions intended for the support team.

This indicates that the search functionality may not correctly enforce the publication or access-control rules applied to customer-facing articles.

## 6. Reproducing the Finding

### Using Firefox Developer Tools

1. Log in to the Relaybox application with the test customer account.
2. Open the Help Centre.
3. Open Developer Tools using `F12`.
4. Select the **Network** tab and filter requests by Fetch/XHR.
5. Search for `Bug`.
6. Locate the request to `/api/articles/suggest?q=Bug`.
7. Inspect the response.
8. Identify the unpublished article and examine its excerpt.

### Using cURL

The endpoint can also be queried from a terminal:

```bash
BASE='https://lab-1792601359673-ui5nrv.labs-app.bugforge.io'

curl -sG "$BASE/api/articles/suggest" \
  --data-urlencode 'q=Bug' | jq .
```

If authentication is required, reproduce the browser request using Firefox's **Copy as cURL** feature and retain the appropriate session headers. Do not publish session cookies or CSRF tokens in a report or public repository.

## 7. Root Cause Analysis

A likely root cause is that the search implementation filters articles by matching their text but does not consistently enforce publication status or authorization.

For example, a vulnerable implementation might conceptually perform the following operation:

```sql
SELECT id, title, category, excerpt, published
FROM articles
WHERE title LIKE '%Bug%'
   OR body LIKE '%Bug%';
```

This query is illustrative, not a confirmed representation of Relaybox's actual backend code.

If the application does not add an appropriate publication and access-control condition, unpublished articles may be included in the results.

A secure implementation should enforce authorization at the server-side query or service layer rather than relying on the frontend to hide unpublished records.

## 8. Security Impact

Potential consequences include:

- Disclosure of internal support procedures.
- Exposure of private escalation codes or other confidential content.
- Access to unpublished knowledge-base articles.
- Leakage of operational information that could support further attacks.

The demonstrated impact is disclosure of a private escalation code through the search response. Other consequences would require separate verification.

## 9. Recommended Remediation

1. Filter unpublished articles from customer-facing search results on the server.
2. Enforce authorization checks for every article returned by search and article-detail endpoints.
3. Separate internal support documentation from public knowledge-base content.
4. Avoid including sensitive internal information in search excerpts.
5. Add regression tests verifying that unpublished articles are not returned to unauthorized customers.
6. Apply consistent access-control rules across listing, search, suggestion, and article-detail endpoints.

For example, the server-side query could include an appropriate publication condition:

```sql
SELECT id, title, category, excerpt
FROM articles
WHERE published = 1
  AND (
    title LIKE '%Bug%'
    OR body LIKE '%Bug%'
  );
```

The actual implementation must also enforce workspace membership and any additional access-control requirements.

## 10. Conclusion

The Relaybox challenge was investigated by inspecting the Help Centre's API traffic and comparing the article-listing endpoint with the search-suggestion endpoint.

The key finding occurred when searching for `Bug` returned an unpublished article containing a private escalation code. The article's `published` value was `0`, yet its sensitive excerpt was accessible in the customer-facing search response.

This behaviour is consistent with an information disclosure vulnerability caused by inadequate filtering or authorization in the search functionality.

**Recovered value:**

```text
bug{LccLBPNmmkVtyoZmvlIxDdzSXeLp1hYf}
```

The recovered value should be submitted to the challenge platform to confirm whether it is the expected solution.

---

**Responsible testing note:** All testing described here was performed against the designated Bugforge challenge environment using a test customer account.