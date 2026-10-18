# Vaultly — Account Takeover

**Challenge:** Vaultly
**Hint:** `Can you take over someone else's account?`

## Description

Vaultly provides several pre-existing demo accounts:

| Account            | Password  |
| ------------------ | --------- |
| `owner@acme.test`  | `vaultly` |
| `admin@acme.test`  | `vaultly` |
| `editor@acme.test` | `vaultly` |
| `viewer@acme.test` | `vaultly` |

The application contains a password-reset functionality under:

```text
/settings/security
```

The password-reset confirmation endpoint does not properly bind the reset token to the account for which it was generated.

Because the `email` parameter is accepted from the client, a valid reset token can be combined with another user's email address to change that user's password.

---

## Step 1 — Login with a Demo Account

Start by logging in with one of the supplied demo accounts.

For example:

```text
Email: owner@acme.test
Password: vaultly
```

After logging in, navigate to:

```text
Settings → Security
```

You should see a section similar to:

```text
Reset your password

Generate a one-time link to set a new password for your account.

[ Email me a reset link ]
```

---

## Step 2 — Generate a Password Reset Link

Click:

```text
Email me a reset link
```

Because this is a sandbox environment, Vaultly exposes the generated reset link directly.

For example:

```text
/reset?token=<RESET_TOKEN>
```

Copy the token.

The token is currently associated with the account that requested the reset.

---

## Step 3 — Reset the Password Normally

Open the reset link.

The password-reset form submits a request to:

```http
POST /api/auth/reset/confirm
```

Capture the request using **Burp Suite**.

A normal request looks like:

```http
POST /api/auth/reset/confirm

token=<RESET_TOKEN>&email=owner%40acme.test&password=<NEW_PASSWORD>
```

The important observation is that the request contains both:

```text
token
email
password
```

---

## Step 4 — Send the Request to Repeater

Right-click the request in Burp Suite and select `Send to Repeater`

In Repeater, keep the valid reset token but change the `email` parameter to another supplied demo account.

For example, if the reset token was generated while logged in as:

```text
owner@acme.test
```

change:

```text
email=owner%40acme.test
```

to:

```text
email=admin%40acme.test
```

Set a new password:

```text
password=vaulty123
```

The resulting body becomes:

```http
token=<VALID_TOKEN>&email=admin%40acme.test&password=vaulty123
```

---

## Step 5 — Send the Modified Request

Click **Send** in Burp Repeater.

If the application accepts the request and redirects to the login page with a message similar to:

```text
Password updated. Please sign in.
```

the password-reset operation has been accepted for the account specified by the modified `email` parameter.

---

## Step 6 — Verify the Account Takeover

Return to the login page.

Try logging in using the target demo account:

```text
Email: admin@acme.test
Password: vaulty123
```

If authentication succeeds, the password of the other demo account has been successfully changed.

The same technique can be tested between the supplied accounts, for example:

```text
owner → admin
owner → editor
owner → viewer
```

or another valid demo-account combination.

---

## Vulnerability

The vulnerable endpoint is:

```text
POST /api/auth/reset/confirm
```

The application accepts a reset token and a client-controlled email address.

The expected secure relationship should be:

```text
Reset Token
     ↓
Account for which token was issued
     ↓
Password reset
```

Instead, the application effectively allows:

```text
Valid Reset Token
        +
Attacker-controlled Email
        ↓
Password reset for supplied account
```

The server fails to ensure that the supplied email belongs to the account associated with the reset token.

---

## Impact

An attacker who obtains a valid password-reset token for their own account can potentially modify the `email` parameter and reset the password of another account.

This can result in:

* Unauthorized password changes
* Account takeover
* Unauthorized access to the victim's account
* Access to resources available to the victim's role

---

## Flag

After successfully taking over the target account in the challenge environment, Vaultly displays the flag in the password-change notification:

```text
bug{GZNAneqqJYFg11nlbCEaIqS0UdEthBaB}
```

---

## Remediation

The reset token must be cryptographically and logically bound to the account for which it was generated.

The server should:

1. Generate a unique, unpredictable reset token.
2. Store the token together with the corresponding user ID.
3. When the token is submitted, identify the user from the server-side token record.
4. Ignore any client-supplied email/user identifier when determining the target account.
5. Verify that the token is valid, unexpired, unused, and associated with the target account.
6. Invalidate the token immediately after successful use.

For example, instead of trusting:

```http
token=<TOKEN>&email=<USER_CONTROLLED_EMAIL>&password=<PASSWORD>
```

the server should effectively process:

```text
TOKEN
 ↓
Server-side token lookup
 ↓
Associated user ID
 ↓
Update that user's password
```

This prevents a valid reset token for one account from being reused to reset another account's password.