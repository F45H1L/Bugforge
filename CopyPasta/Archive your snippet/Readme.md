# CopyPasta — copypasta-012 — Archive your snippet.

## Challenge Overview

- **Challenge:** CopyPasta
- **Platform:** Bugforge
- **Hint:** Archive your snippet.
- **Objective:** Investigate snippet creation and archiving behavior to discover the challenge flag.

## 1. Initial Reconnaissance

The application allows users to create and share code snippets. After registering a test account, I created a snippet with the following details:

| Field | Value |
|---|---|
| Title | Test |
| Language | Markdown |
| Visibility | Public |
| Description | This is a test snippet |
| Snippet ID | `8` |

### Request

```http
POST /api/snippets
Content-Type: application/json
Authorization: Bearer <token>
```

Request body:

```json
{
  "title": "Test",
  "code": "# This is a test snippet\n```\nThis is a test code\n```",
  "language": "markdown",
  "description": "This is a test snippet",
  "is_public": true
}
```

### Response

```json
{
  "id": 8,
  "share_code": "0b0ed100-51be-4f23-96f2-b873b46340a0",
  "message": "Snippet created successfully"
}
```

The server assigned snippet ID `8` and generated a unique share code.

## 2. Investigating the Archive Functionality

The challenge hint was:

> Archive your snippet.

Based on the hint, I inspected the application's network traffic and identified the archive endpoint.

### Request

```http
POST /api/snippets/8/archive
Authorization: Bearer <token>
```

The request did not contain a body.

### Response

```json
{
  "message": "Snippet archived"
}
```

The server returned HTTP `200 OK`, indicating that the archive operation was accepted.

## 3. Inspecting Public Snippets

I visited the public snippets page and observed the following API request:

```http
GET /api/snippets/public
```

The response contained snippets belonging to multiple users, including the `admin` account.

The returned records included fields such as:

- `id`
- `user_id`
- `title`
- `code`
- `is_public`
- `archived`
- `share_code`
- `username`

This helped establish how the application exposed snippet information through its API.

## 4. Retrieving the Archived Snippet

After archiving snippet `8`, I requested the individual snippet endpoint from a private browser session.

### Request

```http
GET /api/snippets/8
```

### Response

```json
{
  "id": 8,
  "user_id": 5,
  "title": "Test",
  "code": "# This is a test snippet\n```\nThis is a test code\n```",
  "language": "markdown",
  "description": "This is a test snippet",
  "is_public": 0,
  "archived": 1,
  "share_code": "0b0ed100-51be-4f23-96f2-b873b46340a0",
  "created_at": "2026-10-15 15:33:07",
  "updated_at": "2026-10-15 15:54:54",
  "username": "test",
  "flag": "bug{dEaCgGzcCQo3FeBteXqRsP1MgsKnOmCp}"
}
```

The response confirmed that:

- The snippet had been archived (`archived: 1`).
- Its visibility had changed to private (`is_public: 0`).
- The API returned a `flag` field containing the challenge flag.

## 5. Flag

```text
bug{dEaCgGzcCQo3FeBteXqRsP1MgsKnOmCp}
```

## 6. Security Analysis

The main finding was that the individual snippet endpoint returned a flag alongside the snippet data.

The response was obtained using a private browser session, which suggests that the endpoint may expose sensitive information without appropriate authorization checks.

However, further testing would be required to conclusively determine the authentication requirements, the intended flag-disclosure mechanism, and whether the behavior constitutes an access-control vulnerability.

### Potential Security Issues

- **Sensitive information disclosure:** The API includes a flag in the snippet response.
- **Access-control validation:** The endpoint should verify whether the requester is authorized to access the requested snippet and its associated sensitive data.
- **Data minimization:** Internal or challenge-sensitive fields should not be included in ordinary API responses unless necessary.

## 7. Recommended Mitigations

1. Enforce server-side authorization checks when retrieving snippets.
2. Ensure private and archived snippets are accessible only to authorized users.
3. Avoid including flags, internal fields, or other sensitive information in general-purpose API responses.
4. Apply consistent access-control rules across snippet listing, retrieval, archiving, and restoration endpoints.
5. Add automated tests for unauthenticated access and cross-user snippet retrieval.

## Conclusion

The CopyPasta challenge was solved by following the hint to archive a snippet, identifying the archive endpoint, and inspecting the individual snippet API response afterward.

The decisive evidence was the `flag` field returned by `GET /api/snippets/8`:

`bug{dEaCgGzcCQo3FeBteXqRsP1MgsKnOmCp}`

The investigation demonstrates the importance of examining API responses and validating authorization behavior rather than relying exclusively on the application's user interface.